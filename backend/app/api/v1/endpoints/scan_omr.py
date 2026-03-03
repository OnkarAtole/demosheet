import cv2
import numpy as np
import traceback
from typing import List, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.answer_key import AnswerKey

router = APIRouter()

# ==============================
# CONFIG
# ==============================

OMR_LAYOUT = [
    {"start": 1, "count": 23, "roi": (0.08, 0.26), "y_start": 0.48},
    {"start": 24, "count": 41, "roi": (0.32, 0.48), "y_start": 0.14},
    {"start": 65, "count": 36, "roi": (0.55, 0.75), "y_start": 0.14},
]

FILL_THRESHOLD = 0.50
MIN_MARKER_AREA = 600


# ==============================
# HELPER
# ==============================

def group_into_rows(b_list: List[Dict]) -> List[List[Dict]]:
    if not b_list:
        return []

    b_list.sort(key=lambda b: b["y"])
    median_h = np.median([b["h"] for b in b_list])
    y_tol = median_h * 0.75

    rows = []
    current = [b_list[0]]

    for b in b_list[1:]:
        if abs(b["y"] - current[0]["y"]) < y_tol:
            current.append(b)
        else:
            current.sort(key=lambda x: x["x"])
            rows.append(current)
            current = [b]

    current.sort(key=lambda x: x["x"])
    rows.append(current)
    return rows


# ==============================
# PROCESS SHEET
# ==============================

def process_sheet(image_bytes: bytes, page_offset: int = 0) -> Dict[str, Any]:

    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return {}

    # 1️⃣ Perspective correction
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)

    thresh_marker = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        51, 10
    )

    contours, _ = cv2.findContours(thresh_marker, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    markers = []
    for c in contours:
        if cv2.contourArea(c) > MIN_MARKER_AREA:
            x, y, w, h = cv2.boundingRect(c)
            ar = w / float(h)
            if 0.8 < ar < 1.2:
                markers.append((x + w // 2, y + h // 2))

    if len(markers) >= 4:
        markers = np.array(markers, dtype="float32")
        rect = np.zeros((4, 2), dtype="float32")

        s = markers.sum(axis=1)
        diff = np.diff(markers, axis=1)

        rect[0] = markers[np.argmin(s)]
        rect[2] = markers[np.argmax(s)]
        rect[1] = markers[np.argmin(diff)]
        rect[3] = markers[np.argmax(diff)]

        (tl, tr, br, bl) = rect

        maxWidth = int(max(np.linalg.norm(br - bl), np.linalg.norm(tr - tl)))
        maxHeight = int(max(np.linalg.norm(tr - br), np.linalg.norm(tl - bl)))

        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]
        ], dtype="float32")

        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(img, M, (maxWidth, maxHeight))
    else:
        warped = img

    # 2️⃣ Threshold
    w_gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    w_blur = cv2.GaussianBlur(w_gray, (3, 3), 0)

    w_thresh = cv2.adaptiveThreshold(
        w_blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        31, 7
    )

    contours, _ = cv2.findContours(w_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    bubbles = []
    h_img, w_img = warped.shape[:2]

    # 3️⃣ Bubble detection
    for c in contours:
        area = cv2.contourArea(c)
        if 200 < area < 1800:
            (xc, yc), radius = cv2.minEnclosingCircle(c)
            inner_radius = int(radius * 0.40)

            mask = np.zeros(w_thresh.shape, dtype="uint8")
            cv2.circle(mask, (int(xc), int(yc)), inner_radius, 255, -1)

            filled = cv2.countNonZero(cv2.bitwise_and(w_thresh, w_thresh, mask=mask))
            total = cv2.countNonZero(mask)

            fill_ratio = filled / float(total) if total > 0 else 0

            bubbles.append({
                "x": int(xc),
                "y": int(yc),
                "f": fill_ratio,
                "h": int(radius * 2)
            })

    results = {}

    # ==============================
    # QUESTION EXTRACTION
    # ==============================

    for col in OMR_LAYOUT:

        y_threshold = h_img * col["y_start"]

        col_bubbles = [
            b for b in bubbles
            if col["roi"][0] * w_img <= b["x"] <= col["roi"][1] * w_img
            and b["y"] > y_threshold
        ]

        rows = group_into_rows(col_bubbles)
        rows = sorted(rows, key=lambda r: np.mean([b["y"] for b in r]))

        if len(rows) < 3:
            continue

        centers = [np.mean([b["y"] for b in r]) for r in rows]
        min_y = min(centers)
        max_y = max(centers)
        expected_gap = (max_y - min_y) / (col["count"] - 1)

        slots = [None] * col["count"]

        for row, center in zip(rows, centers):
            index = int(round((center - min_y) / expected_gap))
            if 0 <= index < col["count"]:
                slots[index] = row

        for i in range(col["count"]):

            q_num = col["start"] + i + page_offset
            row = slots[i]

            if row is None or len(row) < 4:
                results[str(q_num)] = "EMPTY"
                continue

            row = sorted(row[-4:], key=lambda b: b["x"])
            ratios = [b["f"] for b in row]
            sorted_idx = np.argsort(ratios)[::-1]

            top = ratios[sorted_idx[0]]
            second = ratios[sorted_idx[1]]

            if top > FILL_THRESHOLD and (top - second) > 0.12:
                detected_answer = chr(65 + sorted_idx[0])
            else:
                detected_answer = "EMPTY"

            results[str(q_num)] = detected_answer

    # ==============================
    # ROLL NUMBER (VERTICAL LOGIC)
    # ==============================

    roll_number = "EMPTY"

    roll_area = [
        b for b in bubbles
        if 0.05 * w_img < b["x"] < 0.25 * w_img
        and 0.18 * h_img < b["y"] < 0.50 * h_img
    ]

    if roll_area:

        roll_area = sorted(roll_area, key=lambda b: b["x"])

        digit_columns = []
        current_col = [roll_area[0]]
        x_tol = 20

        for b in roll_area[1:]:
            if abs(b["x"] - current_col[0]["x"]) < x_tol:
                current_col.append(b)
            else:
                digit_columns.append(current_col)
                current_col = [b]

        digit_columns.append(current_col)

        digits = []

        for col in digit_columns:

            col = sorted(col, key=lambda b: b["y"])

            if len(col) < 8:
                digits.append("?")
                continue

            y_positions = [b["y"] for b in col]
            min_y = min(y_positions)
            max_y = max(y_positions)
            expected_gap = (max_y - min_y) / 9

            slots = [None] * 10

            for b in col:
                index = int(round((b["y"] - min_y) / expected_gap))
                if 0 <= index <= 9:
                    slots[index] = b

            digit_value = "?"

            for idx, b in enumerate(slots):
                if b and b["f"] > FILL_THRESHOLD:
                    digit_value = str(idx)
                    break

            digits.append(digit_value)

        if digits:
            roll_number = "".join(digits)

    # ==============================
    # EXAM SET
    # ==============================

    exam_set = "EMPTY"

    set_area = [
        b for b in bubbles
        if 0.05 * w_img < b["x"] < 0.25 * w_img
        and b["y"] < 0.15 * h_img
    ]

    if set_area:
        set_area = sorted(set_area, key=lambda b: b["x"])
        ratios = [b["f"] for b in set_area]
        max_idx = np.argmax(ratios)

        if ratios[max_idx] > FILL_THRESHOLD:
            exam_set = chr(65 + max_idx)

    return {
        "answers": results,
        "roll_number": roll_number,
        "exam_set": exam_set
    }


# ==============================
# API ROUTE
# ==============================

@router.post("/scan-omr")
async def scan_omr(
    files: List[UploadFile] = File(...),
    exam_id: int = Form(...),
    db: Session = Depends(get_db),
):
    try:
        answer_key = db.query(AnswerKey).filter(
            AnswerKey.exam_id == exam_id
        ).order_by(AnswerKey.id).all()

        correct_answers = {
            str(i + 1): r.correct_option.strip().upper()
            for i, r in enumerate(answer_key)
        }

        questions_per_page = sum(col["count"] for col in OMR_LAYOUT)

        final_data = {}
        roll_number = "EMPTY"
        exam_set = "EMPTY"

        for idx, file in enumerate(files):
            page_offset = idx * questions_per_page
            page_result = process_sheet(await file.read(), page_offset)
            final_data.update(page_result.get("answers", {}))

            if idx == 0:
                roll_number = page_result.get("roll_number", "EMPTY")
                exam_set = page_result.get("exam_set", "EMPTY")

        score = 0
        wrong_questions = []
        skipped_questions = []
        detailed = {}

        for q, correct in correct_answers.items():

            student = final_data.get(q, "EMPTY")

            if student == correct:
                score += 1
                status = "correct"
            elif student == "EMPTY":
                status = "unanswered"
                skipped_questions.append(q)
            else:
                status = "wrong"
                wrong_questions.append(q)

            detailed[q] = {
                "student": student,
                "correct": correct,
                "result": status
            }

        return {
            "status": "success",
            "data": {
                "roll_number": roll_number,
                "exam_set": exam_set,
                "score": score,
                "total": len(correct_answers),
                "percentage": round((score / len(correct_answers)) * 100, 2),
                "wrong_questions": wrong_questions,
                "unanswered_questions": skipped_questions,
                "detailed_results": detailed
            }
        }

    except Exception as e:
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
# import cv2
# import numpy as np
# import traceback
# from typing import List, Dict, Any
# from fastapi import APIRouter, UploadFile, File, Form, Depends
# from sqlalchemy.orm import Session

# from app.db.session import get_db
# from app.models.answer_key import AnswerKey

# router = APIRouter()

# # ==============================
# # CONFIG
# # ==============================

# OMR_LAYOUT = [
#     {"start": 1, "count": 23, "roi": (0.08, 0.26), "y_start": 0.48},
#     {"start": 24, "count": 41, "roi": (0.32, 0.48), "y_start": 0.14},
#     {"start": 65, "count": 36, "roi": (0.55, 0.75), "y_start": 0.14},
# ]

# FILL_THRESHOLD = 0.50
# MIN_MARKER_AREA = 600


# # ==============================
# # ROW GROUPING
# # ==============================

# def group_into_rows(b_list: List[Dict]) -> List[List[Dict]]:
#     if not b_list:
#         return []

#     b_list.sort(key=lambda b: b["y"])
#     median_h = np.median([b["h"] for b in b_list])
#     y_tol = median_h * 0.75

#     rows = []
#     current = [b_list[0]]

#     for b in b_list[1:]:
#         if abs(b["y"] - current[0]["y"]) < y_tol:
#             current.append(b)
#         else:
#             current.sort(key=lambda x: x["x"])
#             rows.append(current)
#             current = [b]

#     current.sort(key=lambda x: x["x"])
#     rows.append(current)
#     return rows


# # ==============================
# # PROCESS SHEET
# # ==============================

# def process_sheet(image_bytes: bytes, page_offset: int = 0) -> Dict[str, Any]:

#     nparr = np.frombuffer(image_bytes, np.uint8)
#     img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#     if img is None:
#         return {}

#     # ==============================
#     # 1️⃣ Perspective Correction
#     # ==============================

#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     blur = cv2.GaussianBlur(gray, (7, 7), 0)

#     thresh_marker = cv2.adaptiveThreshold(
#         blur, 255,
#         cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#         cv2.THRESH_BINARY_INV,
#         51, 10
#     )

#     contours, _ = cv2.findContours(thresh_marker, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     markers = []
#     for c in contours:
#         area = cv2.contourArea(c)
#         if area > MIN_MARKER_AREA:
#             x, y, w, h = cv2.boundingRect(c)
#             ar = w / float(h)
#             if 0.8 < ar < 1.2:
#                 markers.append((x + w // 2, y + h // 2))

#     if len(markers) >= 4:
#         markers = np.array(markers, dtype="float32")
#         rect = np.zeros((4, 2), dtype="float32")

#         s = markers.sum(axis=1)
#         diff = np.diff(markers, axis=1)

#         rect[0] = markers[np.argmin(s)]
#         rect[2] = markers[np.argmax(s)]
#         rect[1] = markers[np.argmin(diff)]
#         rect[3] = markers[np.argmax(diff)]

#         (tl, tr, br, bl) = rect

#         maxWidth = int(max(np.linalg.norm(br - bl), np.linalg.norm(tr - tl)))
#         maxHeight = int(max(np.linalg.norm(tr - br), np.linalg.norm(tl - bl)))

#         dst = np.array([
#             [0, 0],
#             [maxWidth - 1, 0],
#             [maxWidth - 1, maxHeight - 1],
#             [0, maxHeight - 1]
#         ], dtype="float32")

#         M = cv2.getPerspectiveTransform(rect, dst)
#         warped = cv2.warpPerspective(img, M, (maxWidth, maxHeight))
#     else:
#         warped = img

#     # ==============================
#     # 2️⃣ Adaptive Threshold (ONLY)
#     # ==============================

#     w_gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
#     w_blur = cv2.GaussianBlur(w_gray, (3, 3), 0)

#     w_thresh = cv2.adaptiveThreshold(
#         w_blur, 255,
#         cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#         cv2.THRESH_BINARY_INV,
#         31, 7
#     )

#     contours, _ = cv2.findContours(w_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     bubbles = []
#     final_vis = warped.copy()
#     h_img, w_img = warped.shape[:2]

#     # ==============================
#     # 3️⃣ Bubble Detection (Inner Core Only)
#     # ==============================

#     for c in contours:
#         area = cv2.contourArea(c)
#         if 200 < area < 1800:

#             (xc, yc), radius = cv2.minEnclosingCircle(c)
#             inner_radius = int(radius * 0.40)   # 🔥 key fix

#             mask = np.zeros(w_thresh.shape, dtype="uint8")
#             cv2.circle(mask, (int(xc), int(yc)), inner_radius, 255, -1)

#             filled = cv2.countNonZero(cv2.bitwise_and(w_thresh, w_thresh, mask=mask))
#             total = cv2.countNonZero(mask)

#             fill_ratio = filled / float(total) if total > 0 else 0

#             bubbles.append({
#                 "x": int(xc),
#                 "y": int(yc),
#                 "f": fill_ratio,
#                 "h": int(radius * 2)
#             })

#     results = {}

#     # ==============================
#     # 4️⃣ Stable Slot Mapping
#     # ==============================

#     for col in OMR_LAYOUT:

#         y_threshold = h_img * col["y_start"]

#         col_bubbles = [
#             b for b in bubbles
#             if col["roi"][0] * w_img <= b["x"] <= col["roi"][1] * w_img
#             and b["y"] > y_threshold
#         ]

#         rows = group_into_rows(col_bubbles)
#         rows = sorted(rows, key=lambda r: np.mean([b["y"] for b in r]))

#         if len(rows) < 3:
#             continue

#         centers = [np.mean([b["y"] for b in r]) for r in rows]

#         min_y = min(centers)
#         max_y = max(centers)
#         expected_gap = (max_y - min_y) / (col["count"] - 1)

#         slots = [None] * col["count"]

#         for row, center in zip(rows, centers):
#             index = int(round((center - min_y) / expected_gap))
#             if 0 <= index < col["count"]:
#                 slots[index] = row

#         for i in range(col["count"]):

#             q_num = col["start"] + i + page_offset
#             row = slots[i]

#             if row is None or len(row) < 4:
#                 results[str(q_num)] = "EMPTY"
#                 continue

#             row = sorted(row[-4:], key=lambda b: b["x"])

#             ratios = [b["f"] for b in row]
#             sorted_idx = np.argsort(ratios)[::-1]

#             top = ratios[sorted_idx[0]]
#             second = ratios[sorted_idx[1]]

#             if top > FILL_THRESHOLD and (top - second) > 0.12:
#                 detected_answer = chr(65 + sorted_idx[0])
#             else:
#                 detected_answer = "EMPTY"

#             results[str(q_num)] = detected_answer

#             print(f"[DETECTED] Q{q_num} -> {detected_answer}")

#             for idx, b in enumerate(row):
#                 color = (0, 255, 0) if idx == sorted_idx[0] else (255, 0, 0)
#                 cv2.circle(final_vis, (b["x"], b["y"]), 10, color, 2)

#     cv2.imwrite("debug_final.png", final_vis)

#     return {"answers": results}


# # ==============================
# # API ROUTE
# # ==============================

# @router.post("/scan-omr")
# async def scan_omr(
#     files: List[UploadFile] = File(...),
#     exam_id: int = Form(...),
#     db: Session = Depends(get_db),
# ):
#     try:
#         answer_key = db.query(AnswerKey).filter(
#             AnswerKey.exam_id == exam_id
#         ).order_by(AnswerKey.id).all()

#         correct_answers = {
#             str(i + 1): r.correct_option.strip().upper()
#             for i, r in enumerate(answer_key)
#         }

#         print("\n===== ANSWER KEY FETCHED FROM DB =====")
#         for q, ans in correct_answers.items():
#             print(f"[KEY] Q{q} -> {ans}")

#         questions_per_page = sum(col["count"] for col in OMR_LAYOUT)

#         final_data = {}

#         for idx, file in enumerate(files):
#             page_offset = idx * questions_per_page
#             page_result = process_sheet(await file.read(), page_offset)
#             final_data.update(page_result.get("answers", {}))

#             score = 0
#             wrong_questions = []
#             skipped_questions = []
#             detailed = {}

#             print("\n===== COMPARISON RESULT =====")

#             for q, correct in correct_answers.items():

#                 student = final_data.get(q, "EMPTY")

#                 if student == correct:
#                     score += 1
#                     status = "correct"

#                 elif student == "EMPTY":
#                     status = "unanswered"
#                     skipped_questions.append(q)

#                 else:
#                     status = "wrong"
#                     wrong_questions.append(q)

#                 print(f"Q{q} | Student: {student} | Correct: {correct} | Result: {status}")

#                 detailed[q] = {
#                     "student": student,
#                     "correct": correct,
#                     "result": status
#                 }

#             print(f"\nFINAL SCORE: {score} / {len(correct_answers)}")
#             print(f"WRONG QUESTIONS: {wrong_questions}")
#             print(f"SKIPPED QUESTIONS: {skipped_questions}")

#             return {
#                 "status": "success",
#                 "data": {
#                     "score": score,
#                     "total": len(correct_answers),
#                     "percentage": round((score / len(correct_answers)) * 100, 2),

#                     # 🔥 NOW RETURNING THESE
#                     "wrong_questions": wrong_questions,
#                     "unanswered_questions": skipped_questions,

#                     "detailed_results": detailed
#                 }
# }

#         print("\n===== COMPARISON RESULT =====")

#         for q, correct in correct_answers.items():
#             student = final_data.get(q, "EMPTY")

#             if student == correct:
#                 score += 1
#                 status = "correct"
#             elif student == "EMPTY":
#                 status = "unanswered"
#             else:
#                 status = "wrong"

#             print(f"Q{q} | Student: {student} | Correct: {correct} | Result: {status}")

#             detailed[q] = {
#                 "student": student,
#                 "correct": correct,
#                 "result": status
#             }

#         print(f"\nFINAL SCORE: {score} / {len(correct_answers)}")

#         return {
#             "status": "success",
#             "data": {
#                 "score": score,
#                 "total": len(correct_answers),
#                 "percentage": round((score / len(correct_answers)) * 100, 2),
#                 "detailed_results": detailed
#             }
#         }

#     except Exception as e:
#         traceback.print_exc()
#         return {"status": "error", "message": str(e)}