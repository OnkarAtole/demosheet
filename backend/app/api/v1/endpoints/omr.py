"""
Single File OMR System
FastAPI + OpenCV
Stable Vertical Bubble Detection
"""

import cv2
import numpy as np
import json
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.exam import Exam


router = APIRouter()

# ==============================
# CONFIG
# ==============================
FILL_THRESHOLD = 0.25
FILL_MARGIN = 0.05
MIN_AREA = 150
MAX_AREA = 3000


# ==============================
# OMR PROCESSING
# ==============================
# def process_sheet(image_bytes: bytes, total_questions: int):

#     npimg = np.frombuffer(image_bytes, np.uint8)
#     img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

#     if img is None:
#         raise ValueError("Invalid image")

#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#     blur = cv2.GaussianBlur(gray, (5, 5), 0)

#     thresh = cv2.adaptiveThreshold(
#         blur,
#         255,
#         cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#         cv2.THRESH_BINARY_INV,
#         25,
#         8,
#     )

#     contours, _ = cv2.findContours(
#         thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
#     )

#     bubbles = []

#     for c in contours:
#         area = cv2.contourArea(c)

#         if area < MIN_AREA or area > MAX_AREA:
#             continue

#         (x, y, w, h) = cv2.boundingRect(c)

#         aspect_ratio = w / float(h)

#         # roughly circular
#         if 0.8 <= aspect_ratio <= 1.2:

#             mask = np.zeros(thresh.shape, dtype="uint8")
#             cv2.drawContours(mask, [c], -1, 255, -1)

#             total = cv2.countNonZero(mask)
#             filled = cv2.countNonZero(cv2.bitwise_and(thresh, thresh, mask=mask))

#             fill_ratio = filled / float(total)

#             center_y = y + h // 2

#             bubbles.append((center_y, fill_ratio))

#     # sort vertically
#     bubbles = sorted(bubbles, key=lambda b: b[0])

#     answers = {}
#     question_number = 1

#     # every 4 bubbles = 1 question
#     for i in range(0, len(bubbles), 4):

#         if question_number > total_questions:
#             break

#         group = bubbles[i:i+4]

#         if len(group) < 4:
#             break

#         fills = [b[1] for b in group]

#         max_fill = max(fills)
#         sorted_fills = sorted(fills, reverse=True)

#         if (
#             max_fill > FILL_THRESHOLD
#             and (sorted_fills[0] - sorted_fills[1]) > FILL_MARGIN
#         ):
#             option_index = fills.index(max_fill)
#             answers[str(question_number)] = chr(65 + option_index)
#         else:
#             answers[str(question_number)] = "MULTI/EMPTY"

#         question_number += 1

#     print("\n===== DETECTED ANSWERS =====")
#     print(answers)
#     print("============================\n")

#     debug = {
#         "total_bubbles": len(bubbles),
#         "answers_detected": len(answers),
#     }

#     return answers, debug


def process_sheet(image_bytes: bytes, total_questions: int):

    npimg = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Invalid image")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    thresh = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        25, 8
    )

    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    print("Total contours found:", len(contours))

    bubbles = []

    for c in contours:
        area = cv2.contourArea(c)
        if area < 150 or area > 5000:
            continue

        (x, y, w, h) = cv2.boundingRect(c)
        aspect_ratio = w / float(h)

        if 0.7 <= aspect_ratio <= 1.3:
            mask = np.zeros(thresh.shape, dtype="uint8")
            cv2.drawContours(mask, [c], -1, 255, -1)

            total = cv2.countNonZero(mask)
            filled = cv2.countNonZero(cv2.bitwise_and(thresh, thresh, mask=mask))
            fill_ratio = filled / float(total)

            center_x = x + w // 2
            center_y = y + h // 2

            bubbles.append((center_x, center_y, fill_ratio))

    print("Filtered bubble count:", len(bubbles))

    if not bubbles:
        print("⚠ NO BUBBLES DETECTED")
        return {}, {}

    # Print first 20 fill ratios
    print("Sample fill ratios:", [round(b[2], 3) for b in bubbles[:20]])

    bubbles = sorted(bubbles, key=lambda b: b[1])

    rows = []
    current_row = [bubbles[0]]
    ROW_TOL = 20

    for b in bubbles[1:]:
        if abs(b[1] - current_row[0][1]) < ROW_TOL:
            current_row.append(b)
        else:
            rows.append(current_row)
            current_row = [b]

    rows.append(current_row)

    print("Rows detected:", len(rows))

    answers = {}
    question_number = 1

    for row in rows:
        if len(row) < 4:
            continue

        row = sorted(row, key=lambda b: b[0])
        row = row[:4]

        fills = [b[2] for b in row]

        print(f"Q{question_number} fills:", [round(f, 3) for f in fills])

        max_fill = max(fills)
        sorted_fills = sorted(fills, reverse=True)

        if (
            max_fill > 0.20
            and (sorted_fills[0] - sorted_fills[1]) > 0.03
        ):
            option_index = fills.index(max_fill)
            answers[str(question_number)] = chr(65 + option_index)
        else:
            answers[str(question_number)] = "MULTI/EMPTY"

        question_number += 1

    print("\n===== DETECTED ANSWERS =====")
    print(answers)
    print("============================\n")

    return answers, {}

# ==============================
# FASTAPI ROUTE
# ==============================
@router.post("/scan-omr")
async def scan_omr(
    files: List[UploadFile] = File(...),
    exam_id: int = Form(...),
    db: Session = Depends(get_db),
):

    # 1️⃣ Validate Exam
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    correct_answers = exam.answer_key

    if isinstance(correct_answers, str):
        correct_answers = json.loads(correct_answers)

    correct_answers = {
        str(k): str(v).strip().upper()
        for k, v in correct_answers.items()
    }

    total_questions = len(correct_answers)

    student_answers = {}
    question_offset = 0

    # 2️⃣ Process Pages
    for file in files:
        contents = await file.read()

        extracted_answers, debug = process_sheet(
            contents,
            total_questions=total_questions
        )

        for q_no, ans in extracted_answers.items():
            new_q = str(int(q_no) + question_offset)
            student_answers[new_q] = ans

        question_offset += len(extracted_answers)

    # normalize
    student_answers = {
        str(k): str(v).strip().upper()
        for k, v in student_answers.items()
    }

    # auto convert A/B/C/D → 1/2/3/4 if DB uses numbers
    letter_to_number = {"A": "1", "B": "2", "C": "3", "D": "4"}

    sample_correct = list(correct_answers.values())[0]

    if sample_correct in ["1", "2", "3", "4"]:
        student_answers = {
            k: letter_to_number.get(v, v)
            for k, v in student_answers.items()
        }

    # 3️⃣ Compare
    correct_count = 0
    wrong_questions = []
    unanswered_questions = []
    detailed_results = {}

    for q_no, correct_ans in correct_answers.items():

        student_ans = student_answers.get(q_no)

        if not student_ans or student_ans in ["MULTI/EMPTY", ""]:
            unanswered_questions.append(q_no)
            detailed_results[q_no] = {
                "student": None,
                "correct": correct_ans,
                "result": "unanswered",
            }
            continue

        if student_ans == correct_ans:
            correct_count += 1
            detailed_results[q_no] = {
                "student": student_ans,
                "correct": correct_ans,
                "result": "correct",
            }
        else:
            wrong_questions.append(q_no)
            detailed_results[q_no] = {
                "student": student_ans,
                "correct": correct_ans,
                "result": "wrong",
            }

    total = len(correct_answers)
    percentage = round((correct_count / total) * 100, 2) if total else 0

    print("\n=========== OMR DEBUG ===========")
    print("Student Answers:", student_answers)
    print("Correct Answers:", correct_answers)
    print("Score:", correct_count, "/", total)
    print("=================================\n")

    return {
        "status": "success",
        "data": {
            "score": correct_count,
            "total": total,
            "percentage": percentage,
            "wrong_questions": wrong_questions,
            "unanswered_questions": unanswered_questions,
            "detailed_results": detailed_results,
        },
    }