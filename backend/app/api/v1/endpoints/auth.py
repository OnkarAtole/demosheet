from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserLogin
from app.services.user_service import create_user, get_user_by_email
from app.core.security import verify_password, create_access_token
from app.db.session import get_db

router = APIRouter()


@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, user.email)                      #service

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    return create_user(db, user)


@router.post("/signin")
def signin(user: UserLogin, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)                                      #service

    if not db_user or not verify_password(user.password, db_user.password):            #security
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(db_user.id)})                 #security

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


