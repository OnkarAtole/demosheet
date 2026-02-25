import cv2
import numpy as np
from fastapi import APIRouter, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.answer_key import AnswerKey
from app.models.result import Result
from app.models.exam import Exam
import re
router = APIRouter()


# =============================
# Detect Answers (FIXED VERSION)
# =============================
def detect_answers(image, max_questions):

    height, width = image.shape[:2]

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    thresh = cv2.adaptiveThreshold(
        blur,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        25,
        10,
    )

    detected_answers = {}
    question_index = 1

    # ====== Dynamic Layout Based On Image Size ======
    start_y = int(height * 0.55)
    row_spacing = int(height * 0.035)

    bubble_area_width = int(width * 0.35)
    bubble_start_x = int(width * 0.25)

    option_spacing = int(bubble_area_width / 4)

    bubble_size = int(width * 0.03)

    # ================================================

    for y in range(start_y, height - 50, row_spacing):

        if question_index > max_questions:
            break

        option_pixels = []

        for option_index in range(4):

            x = bubble_start_x + option_index * option_spacing

            roi = thresh[
                y:y + bubble_size,
                x:x + bubble_size
            ]

            if roi.shape[0] == 0 or roi.shape[1] == 0:
                option_pixels.append(0)
                continue

            pixels = cv2.countNonZero(roi)
            option_pixels.append(pixels)

        max_pixel = max(option_pixels)
        filled_option = option_pixels.index(max_pixel)

        print("Q", question_index, "pixels:", option_pixels)

        # Relative detection (better than fixed threshold)
        sorted_pixels = sorted(option_pixels, reverse=True)

        if sorted_pixels[0] > 40 and (sorted_pixels[0] - sorted_pixels[1]) > 20:
            detected_answers[str(question_index)] = chr(65 + filled_option)

        question_index += 1

    return detected_answers, None, "Set 1"
# =============================
# API Endpoint
# =============================
@router.post("/scan-omr")
async def scan_omr(
    exam_id: int = Form(...),
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):

    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": "Exam not found"}
        )

    correct_answers = db.query(AnswerKey).filter(
        AnswerKey.exam_id == exam_id
    ).all()

    if not correct_answers:
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": "Answer key not found"}
        )

    # =============================
    # Prepare answer map
    # =============================
    answer_map = {}
    for row in correct_answers:
        answer_map.setdefault(row.set_name, {})
        # answer_map[row.set_name][str(row.question_key)] = row.correct_option
        question_number = re.search(r'\d+', row.question_key)
        if question_number:
            clean_key = question_number.group()
            answer_map[row.set_name][clean_key] = row.correct_option

    detected_set = list(answer_map.keys())[0]
    correct_set_answers = answer_map[detected_set]

    max_questions = len(correct_set_answers)

    student_answers = {}
    question_offset = 0
    roll_number = None

    # =============================
    # Process Each Page
    # =============================
    for file in files:

        content = await file.read()
        if not content:
            continue

        nparr = np.frombuffer(content, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            continue

        detected, roll, set_name = detect_answers(image, max_questions)

        for q, ans in detected.items():
            new_q = str(int(q) + question_offset)
            student_answers[new_q] = ans

        question_offset += len(detected) if detected else 0

    # =============================
    # Calculate Score
    # =============================
    score = 0

    for q in correct_set_answers:
        if student_answers.get(q) == correct_set_answers.get(q):
            score += 1

    print("===== STUDENT ANSWERS =====")
    print(student_answers)

    print("===== CORRECT ANSWERS =====")
    print(correct_set_answers)

    print("===== SCORE =====")
    print(score)

    result = Result(
        exam_id=exam_id,
        class_id=exam.class_id,
        roll_number=roll_number or "UNKNOWN",
        score=score,
        total_questions=max_questions,
    )

    db.add(result)
    db.commit()

    return {
        "status": "success",
        "data": {
            "score": score,
            "total": max_questions,
            "roll_number": roll_number or "UNKNOWN",
            "set": detected_set,
            "extracted_answers": student_answers
        }
    }