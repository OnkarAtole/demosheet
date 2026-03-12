from sqlalchemy.orm import Session
from app.models.result import Result
from app.models.student import Student


def get_exam_analysis(db: Session, exam_id: int):

    # results = (
    #     db.query(
    #         Result.roll_number,
    #         Result.percentage,
    #         Result.score,
    #         Student.name
    #     )
    #     .join(Student, Student.roll_no == Result.roll_number)
    #     .filter(Result.exam_id == exam_id)
    #     .order_by(Result.percentage.desc())
    #     .all()
    # )
    results = (
        db.query(
            Result.roll_number,
            Result.percentage,
            Result.score,
            Student.name
        )
        .join(
            Student,
            (Student.roll_no == Result.roll_number) &
            (Student.class_id == Result.class_id)
        )
        .filter(Result.exam_id == exam_id)
        .order_by(Result.percentage.desc())
        .all()
    )
    analysis = []

    rank = 1

    for r in results:
        analysis.append({
            "rank": rank,
            "name": r.name,
            "roll_number": r.roll_number,
            "percentage": r.percentage,
            "score": r.score
        })
        rank += 1

    return analysis