"""
=============================================================
 OMR Scan Endpoint  —  FastAPI route
=============================================================
POST /api/v1/omr/scan-omr

Accepts one or two page images (multipart/form-data) plus
an exam_id, runs the full OMR pipeline on each page, compares
the extracted answers against the stored answer key, and
returns a structured JSON result.

Author  : Antigravity / Google Deepmind
Version : 2.0.0  (2026-03-07)
=============================================================
"""

import logging
import traceback
from typing import List

from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.answer_key import AnswerKey
from app.models.exam import Exam
from app.services.omr_pipeline import scan_omr_page

logger = logging.getLogger("omr_endpoint")

router = APIRouter()


# ─────────────────────────────────────────────────────────────
# POST /scan-omr
# ─────────────────────────────────────────────────────────────

@router.post("/scan-omr")
async def scan_omr(
    files: List[UploadFile] = File(...),
    exam_id: int = Form(...),
    db: Session = Depends(get_db),
):
    """
    Scan one or more OMR sheet pages and return the grading result.

    Parameters
    ----------
    files    : one page image per file, uploaded in page order
               (filename sort is used as tie-breaker)
    exam_id  : primary key of the exam in the database
    db       : injected SQLAlchemy session

    Response
    --------
    {
        "status": "success",
        "data": {
            "roll_number":        "0003",
            "exam_set":           "1",
            "score":              80,
            "total":              100,
            "percentage":         80.0,
            "wrong_questions":    [...],
            "unanswered_questions": [...],
            "detailed_results":   {...},
            "debug": {
                "blur_scores":      [float, ...],
                "bubble_counts":    [int, ...],
                "dyn_thresholds":   [float, ...],
                "pages_processed":  int
            }
        }
    }
    """
    try:
        # ── 1. Validate Exam ─────────────────────────────────────────
        exam = db.query(Exam).filter(Exam.id == exam_id).first()
        if not exam:
            return {"status": "error", "message": f"Exam ID {exam_id} not found."}
            
        file = files[0]
        image_bytes = await file.read()

        # ── 2. Process page ──────────────────────────────────────────
        page_result = scan_omr_page(image_bytes, 1)

        if page_result.get("error"):
            return {"status": "error", "message": page_result["error"]}

        final_answers = page_result.get("answers", {})
        roll_number   = page_result.get("roll_number", "EMPTY")
        exam_set      = page_result.get("exam_set", "EMPTY")
        
        debug_info = {
            "blur_score":     round(page_result.get("blur_score", 0), 2),
            "bubble_count":   page_result.get("bubble_count", 0),
            "dyn_threshold":  round(page_result.get("dyn_threshold", 0), 4),
        }

        # ── 3. Final Result Assembly ─────────────────────────────────
        # (Assuming answer key fetching follows)

        # ── 4. Fetch answer key from the database ────────────────────
        set_name = f"Set {exam_set}"
        logger.info("Querying answer key: exam_id=%d  set=%s", exam_id, set_name)

        answer_key_rows = (
            db.query(AnswerKey)
            .filter(AnswerKey.exam_id == exam_id, AnswerKey.set_name == set_name)
            .order_by(AnswerKey.id)
            .all()
        )

        correct_answers: dict = {
            str(i + 1): row.correct_option.strip().upper()
            for i, row in enumerate(answer_key_rows)
        }

        # ── 5. Grade ─────────────────────────────────────────────────
        score    = 0
        wrong    = []
        skipped  = []
        detailed = {}

        logger.info("Detected answers: %s", final_answers)
        logger.info("Roll: %s  Set: %s  Ans-key questions: %d",
                    roll_number, exam_set, len(correct_answers))

        for q_num in range(1, len(correct_answers) + 1):
            q_str   = str(q_num)
            correct = correct_answers.get(q_str)
            student = final_answers.get(q_str, "EMPTY")

            if student == correct:
                score  += 1
                status  = "correct"
            elif student == "EMPTY":
                skipped.append(q_str)
                status = "unanswered"
            else:
                wrong.append(q_str)
                status = "wrong"

            detailed[q_str] = {
                "student": student,
                "correct": correct,
                "result":  status,
            }

        total      = len(correct_answers)
        percentage = round((score / total) * 100, 2) if total else 0.0

        return {
            "status": "success",
            "data": {
                "roll_number":                roll_number,
                "exam_set":                   exam_set,
                "score":                      score,
                "total":                      total,
                "percentage":                 percentage,
                "wrong_questions":            wrong,
                "wrong_questions_count":      len(wrong),
                "unanswered_questions":       skipped,
                "unanswered_questions_count": len(skipped),
                "detailed_results":           detailed,
                "debug":                      debug_info,
            },
        }

    except Exception:
        traceback.print_exc()
        return {"status": "error", "message": "Internal server error. See server logs."}