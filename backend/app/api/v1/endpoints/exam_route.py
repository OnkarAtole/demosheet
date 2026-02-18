from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.exam import Exam
from app.models.subject import Subject
from app.schemas.exam_schema import ExamCreate
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter(prefix="/exams", tags=["Exams"])

@router.post("/")
def create_exam(
    exam_data: ExamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    new_exam = Exam(
        exam_name=exam_data.exam_name,
        class_id=exam_data.class_id,
        roll_no_digit=exam_data.roll_no_digit,
        exam_set=exam_data.exam_set,
        no_of_subject=len(exam_data.subjects)
    )

    db.add(new_exam)
    db.flush()  # Get exam ID before commit

    for sub in exam_data.subjects:
        subject = Subject(
            sub_name=sub.sub_name,
            question_count=sub.question_count,
            exam_id=new_exam.id
        )
        db.add(subject)

    db.commit()

    return {"message": "Exam created successfully"}
