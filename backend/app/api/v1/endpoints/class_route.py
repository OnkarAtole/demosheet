from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.class_schema import ClassCreate, ClassResponse
from app.models.class_model import Class

from app.models.user import User
from app.core.security import get_current_user


router = APIRouter(prefix="/classes", tags=["Classes"])


@router.post("/", response_model=ClassResponse)
def create_class(
    class_data: ClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_class = Class(
    classname=class_data.classname,
    created_by=current_user.id
)


    db.add(new_class)
    db.commit()
    db.refresh(new_class)

    return new_class
