from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.student import Student
from app.schemas.student_schema import StudentCreate, StudentResponse

router = APIRouter(prefix="/students", tags=["Students"])
@router.post("/", response_model=StudentResponse)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):

    # Optional: check if email already exists
    existing_student = db.query(Student).filter(Student.email == student.email).first()
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
