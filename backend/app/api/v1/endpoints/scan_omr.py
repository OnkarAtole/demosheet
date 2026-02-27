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
FILL_THRESHOLD = 0.12
FILL_MARGIN = 0.02
MIN_AREA = 150
MAX_AREA = 5000
ROW_TOL = 90


# ==============================
# OMR PROCESSING
# ==============================


# extra function to process each sheet image and extract answers
# def warp_omr_sheet(image):

#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     blur = cv2.GaussianBlur(gray, (5, 5), 0)

#     edged = cv2.Canny(blur, 50, 150)

#     contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     if not contours:
#         return image

#     # page = max(contours, key=cv2.contourArea)
#     contours = sorted(contours, key=cv2.contourArea, reverse=True)

#     page = None

#     for c in contours:
#         peri = cv2.arcLength(c, True)
#         approx = cv2.approxPolyDP(c, 0.02 * peri, True)

#         if len(approx) == 4:
#             page = approx
#             break

#     if page is None:
#         return image

#     # peri = cv2.arcLength(page, True)
#     # approx = cv2.approxPolyDP(page, 0.02 * peri, True)

#     # if len(approx) != 4:
#     #     return image

#     # pts = approx.reshape(4, 2)
#     pts = page.reshape(4, 2)
#     rect = np.zeros((4, 2), dtype="float32")

#     s = pts.sum(axis=1)
#     rect[0] = pts[np.argmin(s)]
#     rect[2] = pts[np.argmax(s)]

#     diff = np.diff(pts, axis=1)
#     rect[1] = pts[np.argmin(diff)]
#     rect[3] = pts[np.argmax(diff)]

#     (tl, tr, br, bl) = rect

#     widthA = np.linalg.norm(br - bl)
#     widthB = np.linalg.norm(tr - tl)
#     maxWidth = int(max(widthA, widthB))

#     heightA = np.linalg.norm(tr - br)
#     heightB = np.linalg.norm(tl - bl)
#     maxHeight = int(max(heightA, heightB))

#     dst = np.array([
#         [0, 0],
#         [maxWidth - 1, 0],
#         [maxWidth - 1, maxHeight - 1],
#         [0, maxHeight - 1]
#     ], dtype="float32")

#     M = cv2.getPerspectiveTransform(rect, dst)
#     warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

#     return warped

def warp_omr_sheet(image):

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    edged = cv2.Canny(blur, 50, 150)

    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return image

    # contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # page = None

    # for c in contours:
    #     peri = cv2.arcLength(c, True)
    #     approx = cv2.approxPolyDP(c, 0.02 * peri, True)

    #     if len(approx) == 4:
    #         page = approx
    #         break

    # if page is None:
    #     return image

    h, w = image.shape[:2]
    image_area = h * w

    page = None

    for c in contours:
        area = cv2.contourArea(c)

        print("Contour area:", area)  #dummy print to debug contour areas
        # keep only large contours (page candidates)
        if area < image_area * 0.4:
            continue

        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        if len(approx) == 4:
            page = approx
            break

    if page is None:
        return image

    pts = page.reshape(4, 2)

    rect = np.zeros((4, 2), dtype="float32")

    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    (tl, tr, br, bl) = rect

    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = int(max(widthA, widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = int(max(heightA, heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped
def process_sheet(image_bytes: bytes, total_questions: int):

    npimg = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Invalid image")

    img = warp_omr_sheet(img)
    # temp debug
    cv2.imwrite("debug_warp.jpg", img)

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
    cv2.imwrite("debug_thresh.jpg", thresh)
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
    # if len(bubbles) == 0:
    #     return {}
    # rows = []
    # current_row = [bubbles[0]]

    # for b in bubbles[1:]:
    #     if abs(b[1] - current_row[0][1]) < ROW_TOL:
    #         current_row.append(b)
    #     else:
    #         rows.append(current_row)
    #         current_row = [b]

    # rows.append(current_row)
    # -------- COLUMN SPLIT --------
    bubbles = sorted(bubbles, key=lambda b: b[0])

    columns = []
    current_col = [bubbles[0]]

    COL_TOL = 120

    for b in bubbles[1:]:
        if abs(b[0] - current_col[0][0]) < COL_TOL:
            current_col.append(b)
        else:
            columns.append(current_col)
            current_col = [b]

    columns.append(current_col)

    rows = []

    for col in columns:
        col = sorted(col, key=lambda b: b[1])

        current_row = [col[0]]

        for b in col[1:]:
            if abs(b[1] - current_row[0][1]) < ROW_TOL:
                current_row.append(b)
            else:
                rows.append(current_row)
                current_row = [b]

        rows.append(current_row)

    answers = {}
    question_number = 1

    for row in rows:

        if question_number > total_questions:
            break

        if len(row) < 4:
            continue

        # row = sorted(row, key=lambda b: b[0])
        # row = row[:4]
        row = sorted(row, key=lambda b: b[0])

        # take 4 most circular bubbles
        # row = sorted(row, key=lambda b: b[2], reverse=True)[:4]
        row = sorted(row, key=lambda b: b[0])

        # restore left→right order
        row = sorted(row, key=lambda b: b[0])
        fills = [b[2] for b in row]
        max_fill = max(fills)
        sorted_fills = sorted(fills, reverse=True)
        # fills = [b[2] for b in row]
        if max(fills) < 0.08:
            answers[str(question_number)] = "MULTI/EMPTY"
            question_number += 1
            continue

        

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
    # print("Exam query result:", exam)
    print("========== DEBUG SCAN ==========")
    print("Incoming exam_id:", exam_id)

    all_keys = db.query(AnswerKey).all()
    print("All exam_ids in answer_keys:", [k.exam_id for k in all_keys])

    # answer_key_rows = db.query(AnswerKey).filter(
    #     AnswerKey.exam_id == exam_id
    # ).all()
    # answer_key_rows = sorted(answer_key_rows, key=lambda x: x.id)
  
    print("================================")
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    # 2️⃣ Get answer key from AnswerKey table
    answer_key_rows = db.query(AnswerKey).filter(
    AnswerKey.exam_id == exam_id
    ).order_by(AnswerKey.id).all()

    if not answer_key_rows:
        raise HTTPException(status_code=404, detail="Answer key not found")

    # 🔥 Convert DB rows into numeric mapping (1,2,3...)
    # correct_answers = {
    #     str(index): row.correct_option.strip().upper()
    #     for index, row in enumerate(answer_key_rows, start=1)
    # }
    answer_key_rows = sorted(
    answer_key_rows,
    key=lambda x: int(x.question_key.split("-")[-1])
    )

    correct_answers = {
        str(i + 1): row.correct_option.strip().upper()
        for i, row in enumerate(answer_key_rows)
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