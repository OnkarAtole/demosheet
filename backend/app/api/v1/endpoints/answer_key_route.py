from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.answer_key import AnswerKey
from app.schemas.answer_key import AnswerKeyCreate
from app.models.exam import Exam
from app.core.security import get_current_user
from app.models.user import User
from app.models.class_model import Class
router = APIRouter(prefix="/answer-key", tags=["Answer Key"])


# ✅ Save Answer Key
@router.post("/{exam_id}")
def save_answer_key(
    exam_id: int,
    payload: AnswerKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    exam = db.query(Exam).join(Class).filter(
    Exam.id == exam_id,
    Class.created_by == current_user.id
).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    # 🔥 Delete old answer key (if editing)
    db.query(AnswerKey).filter(
        AnswerKey.exam_id == exam_id
    ).delete()

    for set_name, questions in payload.answers.items():
        for question_key, option in questions.items():
            answer = AnswerKey(
                exam_id=exam_id,
                set_name=set_name,
                question_key=question_key,
                correct_option=option,
            )
            db.add(answer)

    db.commit()

    return {"message": "Answer key saved successfully"}


@router.get("/{exam_id}")
def get_answer_key(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    answers = db.query(AnswerKey).filter(
        AnswerKey.exam_id == exam_id
    ).all()

    if not answers:
        return {}   # return empty instead of error

    grouped_answers = {}

    for row in answers:
        if row.set_name not in grouped_answers:
            grouped_answers[row.set_name] = {}

        grouped_answers[row.set_name][row.question_key] = row.correct_option

    return grouped_answers

