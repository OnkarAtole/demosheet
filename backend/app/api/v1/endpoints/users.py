from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.core.security import get_current_user  # your JWT dependency

router = APIRouter()

@router.get("/me")
def get_logged_user(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email
    }

from app.core.security import get_password_hash

@router.put("/me")
def update_logged_user(
    update_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.name = update_data.get("name", current_user.name)
    current_user.email = update_data.get("email", current_user.email)

    if update_data.get("password"):
        current_user.password = get_password_hash(update_data["password"])

    db.commit()
    db.refresh(current_user)

    return {"message": "Profile updated successfully"}