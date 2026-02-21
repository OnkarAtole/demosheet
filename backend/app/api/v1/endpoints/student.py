
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.student import Student
from app.schemas.student_schema import StudentCreate, StudentResponse
from app.models import student
from fastapi.responses import FileResponse  
import os 

router = APIRouter(prefix="/students", tags=["Students"])
@router.post("/", response_model=StudentResponse)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):

    # Optional: check if email already exists
    # existing_student = db.query(Student).filter(Student.email == student.email).first()
    # ✅ CHANGED
    existing_student = db.query(Student).filter(
        Student.email == student.email,
        Student.class_id == student.class_id
    ).first()
    if existing_student:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_student = Student(
        name=student.name,
        roll_no=student.roll_no,
        email=student.email,
        class_id=student.class_id
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return new_student
@router.get("/class/{class_id}", response_model=List[StudentResponse])
def get_students_by_class(class_id: int, db: Session = Depends(get_db)):

    students = db.query(Student).filter(Student.class_id == class_id).all()

    return students


@router.post("/bulk/")
def bulk_create_students(
    students: List[StudentCreate],
    db: Session = Depends(get_db)
):
    created = 0

    for student in students:
        # existing = db.query(Student).filter(Student.email == student.email).first()
        existing = db.query(Student).filter(
            Student.email == student.email,
            Student.class_id == student.class_id
        ).first()
        if existing:
            continue

        new_student = Student(
            name=student.name,
            roll_no=student.roll_no,
            email=student.email,
            class_id=student.class_id
        )

        db.add(new_student)
        created += 1

    db.commit()

    return {"created": created}

# @router.get("/demo")
# def download_student_demo():
#     BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#     file_path = os.path.join(BASE_DIR, "static", "student_demo.xlsx")

#     if not os.path.exists(file_path):
#         raise HTTPException(status_code=404, detail="Demo file not found")

#     return FileResponse(
#         path=file_path,
#         filename="student_demo.xlsx",
#         media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     )

@router.get("/demo")
def download_student_demo():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(BASE_DIR, "static", "student_demo.xlsx")

    print("BASE_DIR:", BASE_DIR)
    print("FILE_PATH:", file_path)
    print("FILE_EXISTS:", os.path.exists(file_path))

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Demo file not found")

    return FileResponse(
        path=file_path,
        filename="student_demo.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )