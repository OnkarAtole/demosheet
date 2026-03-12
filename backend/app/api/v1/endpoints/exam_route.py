from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.exam import Exam
from app.models.subjects import Subject
from app.schemas.exam import ExamCreate
from app.models.user import User
from app.models.result import Result
from fastapi.responses import FileResponse
import pandas as pd
from app.core.security import get_current_user
from app.models.class_model import Class
from sqlalchemy import func
from app.models.student import Student
from app.utils.pro_omr_generator import generate_pro_omr
from io import BytesIO
from fastapi.responses import StreamingResponse


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

    total_q = sum(sub.question_count for sub in exam_data.subjects)
    new_exam.total_pages = 2 if total_q > 146 else 1

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
            "total_pages": exam.total_pages or 1,
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

from io import BytesIO
from fastapi.responses import StreamingResponse

@router.get("/export-results/{exam_id}")
def export_results(exam_id: int, db: Session = Depends(get_db)):
    try:
        
        # results = db.query(Result).filter(Result.exam_id == exam_id).all()
        results = (
    db.query(Result, Student)
    .join(
        Student,
        (Student.roll_no == Result.roll_number) &
        (Student.class_id == Result.class_id)
    )
    .filter(Result.exam_id == exam_id)
    .all()
)

        if not results:
            raise HTTPException(status_code=404, detail="No results found")

        data = []
        # for r in results:
        for r, s in results:
            data.append({
                "Roll No": r.roll_number,
                "Name": s.name,
                "Set": r.exam_set,
                "Score": r.score,
                "Total Questions": r.total_questions,
                "Percentage": r.percentage
            })

        df = pd.DataFrame(data)

        output = BytesIO()
        # df.to_excel(output, index=False, engine="openpyxl")
        # output.seek(0)
        # Write dataframe
        from openpyxl import load_workbook
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Results")

            worksheet = writer.sheets["Results"]

            # Auto adjust column width based on header + content
            for column_cells in worksheet.columns:
                max_length = 0
                column = column_cells[0].column_letter

                for cell in column_cells:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass

                adjusted_width = max_length + 2
                worksheet.column_dimensions[column].width = adjusted_width
                # ---------- BOLD HEADER ----------
                from openpyxl.styles import Font
                for cell in worksheet[1]:
                    cell.font = Font(bold=True)


                # ---------- CENTER ALIGN DATA ----------
                from openpyxl.styles import Alignment
                for row in worksheet.iter_rows(min_row=2):
                    for cell in row:
                        cell.alignment = Alignment(horizontal="center")

        output.seek(0)

        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=results_{exam_id}.xlsx"
            }
        )

    except Exception as e:
        print("EXPORT RESULTS ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))