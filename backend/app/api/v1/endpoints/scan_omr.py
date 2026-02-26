"""
OMR V2 - Corrected Version
FastAPI + OpenCV
Uses AnswerKey table properly
"""

import cv2
import numpy as np
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.exam import Exam
from app.models.answer_key import AnswerKey

router = APIRouter()

# ==============================
# CONFIG
# ==============================
FILL_THRESHOLD = 0.20
FILL_MARGIN = 0.03
MIN_AREA = 150
MAX_AREA = 5000
ROW_TOL = 20


# ==============================
# OMR PROCESSING
# ==============================
def process_sheet(image_bytes: bytes, total_questions: int):

    npimg = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Invalid image")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    thresh = cv2.adaptiveThreshold(
        blur,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        25,
        8,
    )

    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    bubbles = []

    for c in contours:
        area = cv2.contourArea(c)
        if area < MIN_AREA or area > MAX_AREA:
            continue

        (x, y, w, h) = cv2.boundingRect(c)
        aspect_ratio = w / float(h)

        if 0.7 <= aspect_ratio <= 1.3:

            mask = np.zeros(thresh.shape, dtype="uint8")
            cv2.drawContours(mask, [c], -1, 255, -1)

            total = cv2.countNonZero(mask)
            filled = cv2.countNonZero(
                cv2.bitwise_and(thresh, thresh, mask=mask)
            )

            fill_ratio = filled / float(total)

            center_x = x + w // 2
            center_y = y + h // 2

            bubbles.append((center_x, center_y, fill_ratio))

    if not bubbles:
        print("⚠ NO BUBBLES DETECTED")
        return {}

    # Sort top to bottom
    # bubbles = sorted(bubbles, key=lambda b: b[1])

    # rows = []
    # current_row = [bubbles[0]]

    # for b in bubbles[1:]:
    #     if abs(b[1] - current_row[0][1]) < ROW_TOL:
    #         current_row.append(b)
    #     else:
    #         rows.append(current_row)
    #         current_row = [b]

    # rows.append(current_row)

    # answers = {}
    # question_number = 1

    # for row in rows:

    #     if question_number > total_questions:
    #         break

    #     if len(row) < 4:
    #         continue

    #     row = sorted(row, key=lambda b: b[0])
    #     row = row[:4]

    #     fills = [b[2] for b in row]

    #     max_fill = max(fills)
    #     sorted_fills = sorted(fills, reverse=True)

    #     if (
    #         max_fill > FILL_THRESHOLD
    #         and (sorted_fills[0] - sorted_fills[1]) > FILL_MARGIN
    #     ):
    #         option_index = fills.index(max_fill)
    #         answers[str(question_number)] = chr(65 + option_index)
    #     else:
    #         answers[str(question_number)] = "MULTI/EMPTY"

    #     question_number += 1
    # Sort by Y (top to bottom)
    bubbles = sorted(bubbles, key=lambda b: b[1])
    
    # Split into left and right columns
    image_width = img.shape[1]
    mid_x = image_width // 2
    
    left_column = [b for b in bubbles if b[0] < mid_x]
    right_column = [b for b in bubbles if b[0] >= mid_x]
    
    columns = [left_column, right_column]
    
    answers = {}
    question_number = 1
    
    for column in columns:
    
        column = sorted(column, key=lambda b: b[1])
    
        rows = []
        current_row = [column[0]]
    
        for b in column[1:]:
            if abs(b[1] - current_row[0][1]) < ROW_TOL:
                current_row.append(b)
            else:
                rows.append(current_row)
                current_row = [b]
    
        rows.append(current_row)
    
        for row in rows:
    
            if len(row) < 4:
                continue
    
            row = sorted(row, key=lambda b: b[0])
            row = row[:4]
    
            fills = [b[2] for b in row]
    
            max_fill = max(fills)
            sorted_fills = sorted(fills, reverse=True)
    
            if (
                max_fill > FILL_THRESHOLD
                and (sorted_fills[0] - sorted_fills[1]) > FILL_MARGIN
            ):
                option_index = fills.index(max_fill)
                answers[str(question_number)] = chr(65 + option_index)
            else:
                answers[str(question_number)] = "MULTI/EMPTY"
    
            question_number += 1

    print("Detected answers:", answers)

    return answers


# ==============================
# FASTAPI ROUTE
# ==============================
@router.post("/scan-omr")
async def scan_omr(
    files: List[UploadFile] = File(...),
    exam_id: int = Form(...),
    db: Session = Depends(get_db),
):

    # 1️⃣ Validate exam
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    # 2️⃣ Get answer key from AnswerKey table
    answer_key_rows = db.query(AnswerKey).filter(
        AnswerKey.exam_id == exam_id
    ).order_by(AnswerKey.id).all()

    if not answer_key_rows:
        raise HTTPException(status_code=404, detail="Answer key not found")

    # 🔥 Convert DB rows into numeric mapping (1,2,3...)
    correct_answers = {
        str(index): row.correct_option.strip().upper()
        for index, row in enumerate(answer_key_rows, start=1)
    }

    total_questions = len(correct_answers)

    student_answers = {}
    question_offset = 0

    # 3️⃣ Process images
    for file in files:
        contents = await file.read()

        extracted = process_sheet(
            contents,
            total_questions=total_questions
        )

        for q_no, ans in extracted.items():
            new_q = str(int(q_no) + question_offset)
            student_answers[new_q] = ans

        question_offset += len(extracted)

    # Normalize
    student_answers = {
        str(k): str(v).strip().upper()
        for k, v in student_answers.items()
    }

    # 4️⃣ Compare
    correct_count = 0
    wrong_questions = []
    unanswered_questions = []
    detailed_results = {}

    for q_no, correct_ans in correct_answers.items():

        student_ans = student_answers.get(q_no)

        if not student_ans or student_ans == "MULTI/EMPTY":
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

    print("\n===== FINAL DEBUG =====")
    print("Student:", student_answers)
    print("Correct:", correct_answers)
    print("Score:", correct_count, "/", total)
    print("=======================\n")

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