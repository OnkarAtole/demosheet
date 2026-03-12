from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.result_service import get_exam_analysis

router = APIRouter()

@router.get("/analysis/{exam_id}")
def exam_analysis(exam_id: int, db: Session = Depends(get_db)):
    return get_exam_analysis(db, exam_id)