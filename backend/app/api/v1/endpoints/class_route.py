from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.class_schema import ClassCreate, ClassResponse
from app.models.class_model import Class

from app.models.user import User
from app.core.security import get_current_user
from app.models.student import Student

router = APIRouter(prefix="/classes", tags=["Classes"])


# @router.post("/", response_model=ClassResponse,)
# def create_class(
#     class_data: ClassCreate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     new_class = Class(
#     classname=class_data.classname,
#     created_by=current_user.id
# )


#     db.add(new_class)
#     db.commit()
#     db.refresh(new_class)

#     return new_class

# @router.post("/", response_model=ClassResponse)
# def create_class(
#     class_data: ClassCreate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     new_class = Class(
#         classname=class_data.classname,
#         created_by=current_user.id
#     )

#     db.add(new_class)
#     db.commit()
#     db.refresh(new_class)

#     # 🔥 Return full response including student_count
#     return {
#         "id": new_class.id,
#         "classname": new_class.classname,
#         "created_by": new_class.created_by,
#         "created_at": new_class.created_at,
#         "student_count": 0
#     }
@router.post("/", response_model=ClassResponse)
def create_class(
    class_data: ClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
   
    normalized_name = class_data.classname.strip()

   
    existing_class = db.query(Class).filter(
        Class.classname.ilike(normalized_name),
        Class.created_by == current_user.id
    ).first()

    if existing_class:
        raise HTTPException(
            status_code=400,
            detail="Class with this name already exists"
        )

    
    new_class = Class(
        classname=normalized_name,
        created_by=current_user.id
    )

    db.add(new_class)
    db.commit()
    db.refresh(new_class)

    return {
        "id": new_class.id,
        "classname": new_class.classname,
        "created_by": new_class.created_by,
        "created_at": new_class.created_at,
        "student_count": 0
    }

@router.get("/{class_id}", response_model=ClassResponse)
def get_class(class_id: int, db: Session = Depends(get_db)):
    class_instance = db.query(Class).filter(Class.id == class_id).first()
    if not class_instance:
        raise HTTPException(status_code=404, detail="Class not found")
    return class_instance


@router.get("/", response_model=list[ClassResponse])
def list_classes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    classes = db.query(Class).filter(
        Class.created_by == current_user.id
    ).all()

    result = []

    for class_instance in classes:
        student_count = db.query(Student).filter(
            Student.class_id == class_instance.id
        ).count()

        result.append({
            "id": class_instance.id,
            "classname": class_instance.classname,
            "created_by": class_instance.created_by,
            "created_at": class_instance.created_at,
            "student_count": student_count
        })

    return result
