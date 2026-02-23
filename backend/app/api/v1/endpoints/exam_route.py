from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.exam import Exam
from app.models.subjects import Subject
from app.schemas.exam import ExamCreate
from app.models.user import User
from app.core.security import get_current_user
from app.models.class_model import Class
from sqlalchemy import func
from app.models.student import Student
from app.utils.pro_omr_generator import generate_pro_omr

router = APIRouter(prefix="/exams", tags=["Exams"])

# @router.post("/")
# def create_exam(
#     exam_data: ExamCreate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
    
#     new_exam = Exam(
#         exam_name=exam_data.exam_name,
#         class_id=exam_data.class_id,
#         roll_no_digit=exam_data.roll_no_digit,
#         exam_set=exam_data.exam_set,
#         no_of_subject=len(exam_data.subjects)
#     )

#     db.add(new_exam)
#     db.flush()  # Get exam ID before commit

#     for sub in exam_data.subjects:
#         subject = Subject(
#             sub_name=sub.sub_name,
#             question_count=sub.question_count,
#             exam_id=new_exam.id
#         )
#         db.add(subject)

#     db.commit()

#     return {"message": "Exam created successfully"}


@router.post("/")
def create_exam(
    exam_data: ExamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # 🔥 Check if class belongs to current user
    class_instance = db.query(Class).filter(
        Class.id == exam_data.class_id,
        Class.created_by == current_user.id
    ).first()

    if not class_instance:
        raise HTTPException(status_code=403, detail="Not authorized to create exam for this class")

    new_exam = Exam(
        exam_name=exam_data.exam_name,
        class_id=exam_data.class_id,
        roll_no_digit=exam_data.roll_no_digit,
        exam_date=exam_data.exam_date,
        exam_set=exam_data.exam_set,
        no_of_subject=len(exam_data.subjects)
    )

    db.add(new_exam)
    db.flush()

    for sub in exam_data.subjects:
        subject = Subject(
            sub_name=sub.sub_name,
            question_count=sub.question_count,
            exam_id=new_exam.id
        )
        db.add(subject)

    db.commit()

    return {"message": "Exam created successfully"}


# @router.get("/")
# def get_exams(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     exams = (
#         db.query(
#             Exam.id,
#             Exam.exam_name,
#             Exam.exam_date,
#             Class.classname.label("class_name"),
#             func.count(Student.id).label("student_count")
#         )
#         .join(Class, Exam.class_id == Class.id)
#         .outerjoin(Student, Student.class_id == Class.id)
#         .filter(Class.created_by == current_user.id)
#         .group_by(Exam.id, Class.classname)
#         .order_by(Exam.exam_date.desc())
#         .all()
#     )

#     return [
#     {
#         "id": exam.id,
#         "exam_name": exam.exam_name,
#         "exam_date": exam.exam_date,
#         "class_name": exam.class_name,
#         "student_count": exam.student_count
#     }
#     for exam in exams
# ]

@router.get("/")
def get_exams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    exams = (
        db.query(Exam)
        .join(Class)
        .filter(Class.created_by == current_user.id)
        .order_by(Exam.exam_date.desc())
        .all()
    )

    result = []

    for exam in exams:
        student_count = db.query(Student).filter(
            Student.class_id == exam.class_id
        ).count()

        result.append({
            "id": exam.id,
            "exam_name": exam.exam_name,
            "exam_date": exam.exam_date,
            "exam_set": exam.exam_set,
            "class_name": exam.class_ref.classname,
            "student_count": student_count,
            "subjects": [
                {
                    "name": sub.sub_name,
                    "questions": sub.question_count
                }
                for sub in exam.subjects
            ]
        })

    return result




# @router.get("/generate-omr/{exam_id}")
# def generate_omr(exam_id: int, db: Session = Depends(get_db)):
#     exam = db.query(Exam).filter(Exam.id == exam_id).first()
#     pdf = generate_pro_omr(exam)

#     return StreamingResponse(
#         pdf,
#         media_type="application/pdf",
#         headers={
#             "Content-Disposition": f"attachment; filename=OMR_{exam.exam_name}.pdf"
#         }
#     )


@router.get("/generate-omr/{exam_id}")
def generate_omr(exam_id: int, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    # 🔥 Now function returns 2 values
    pdf_buffer, total_pages = generate_pro_omr(exam)

    # 🔥 Save page count in DB
    exam.total_pages = total_pages
    db.commit()

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=OMR_{exam.exam_name}.pdf"
        }
    )