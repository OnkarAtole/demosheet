from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserLogin
from app.services.user_service import create_user, get_user_by_email
from app.core.security import verify_password, create_access_token
from app.db.session import get_db

from app.schemas.otp import VerifyOTPRequest
from app.core.email import send_otp_email


# my change

# forget password
import random
import bcrypt
from datetime import datetime, timedelta
from app.schemas.otp import SendOTPRequest, VerifyOTPRequest
from app.schemas.password import ResetPasswordRequest
from app.core.security import get_password_hash
from app.core.email import send_otp_email
from app.models.email_otp import EmailOTP


router = APIRouter()

def generate_otp():
    return str(random.randint(100000, 999999))


# .otp generation and verification logic
@router.post("/send-otp")
def send_otp(data: SendOTPRequest, db: Session = Depends(get_db)):

    # Check if user already exists
    existing_user = get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Delete old OTP if exists
    db.query(EmailOTP).filter(EmailOTP.email == data.email).delete()

    otp = generate_otp()
    expiry_time = datetime.utcnow() + timedelta(minutes=5)

    # new_otp = EmailOTP(
    #     email=data.email,
    #     otp=otp,
    #     expires_at=expiry_time
    # )

    # Hash the OTP for security
    hashed_otp = bcrypt.hashpw(
    otp.encode('utf-8'),
    bcrypt.gensalt()
).decode('utf-8')

    new_otp = EmailOTP(
        email=data.email,
        otp_hash=hashed_otp,
        expires_at=expiry_time
    )

    db.add(new_otp)
    db.commit()
    send_otp_email(data.email, otp)

    return {"message": "OTP sent successfully"}


@router.post("/verify-otp")
def verify_otp(data: VerifyOTPRequest, db: Session = Depends(get_db)):

    otp_record = db.query(EmailOTP).filter(
        EmailOTP.email == data.email
    ).order_by(EmailOTP.id.desc()).first()

    if not otp_record:
        raise HTTPException(status_code=400, detail="OTP not found")

    if otp_record.is_verified:
        raise HTTPException(status_code=400, detail="OTP already verified")

    if otp_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")

    if otp_record.attempts >= 5:
        raise HTTPException(status_code=400, detail="Too many attempts")

    # if otp_record.otp != data.otp:
    if not bcrypt.checkpw(data.otp.encode(),otp_record.otp_hash.encode()):
        otp_record.attempts += 1
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid OTP")

    otp_record.is_verified = True
    db.commit()

    return {"message": "OTP verified successfully"}



@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = get_user_by_email(db, user.email)

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check OTP verification
    otp_record = db.query(EmailOTP).filter(
        EmailOTP.email == user.email
    ).order_by(EmailOTP.id.desc()).first()

    if not otp_record or not otp_record.is_verified:
        raise HTTPException(status_code=400, detail="Email not verified")

    # Create user
    new_user = create_user(db, user)

    # Delete OTP record after successful registration
    db.delete(otp_record)
    db.commit()

    return new_user





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

# logic for forgot password and reset password
@router.post("/forgot-password/send-otp")
def forgot_password_send_otp(data: SendOTPRequest, db: Session = Depends(get_db)):

    user = get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = str(random.randint(100000, 999999))

    otp_record = db.query(EmailOTP).filter(
        EmailOTP.email == data.email
    ).order_by(EmailOTP.id.desc()).first()

    if otp_record:
        # otp_record.otp = otp
        otp_record.otp_hash = bcrypt.hashpw(
            otp.encode(),
            bcrypt.gensalt()
            ).decode()
        otp_record.is_verified = False
        otp_record.attempts = 0
        otp_record.expires_at = datetime.utcnow() + timedelta(minutes=5)
    else:
        # otp_record = EmailOTP(
        #     email=data.email,
        #     otp=otp,
        #     expires_at=datetime.utcnow() + timedelta(minutes=5)
        # )otp_record = EmailOTP(
        otp_record = EmailOTP(
            email=data.email,
            otp_hash=bcrypt.hashpw(
                otp.encode(),
                bcrypt.gensalt()
            ).decode('utf-8'),
             expires_at=datetime.utcnow() + timedelta(minutes=5)
        )
        db.add(otp_record)

    db.commit()

    send_otp_email(data.email, otp)

    return {"message": "OTP sent successfully"}


# verify otp for forgot password
@router.post("/forgot-password/verify-otp")
def forgot_password_verify_otp(data: VerifyOTPRequest, db: Session = Depends(get_db)):

    otp_record = db.query(EmailOTP).filter(
        EmailOTP.email == data.email
    ).order_by(EmailOTP.id.desc()).first()

    if not otp_record:
        raise HTTPException(status_code=400, detail="OTP not found")

    if otp_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")

    if otp_record.attempts >= 5:
        raise HTTPException(status_code=400, detail="Too many attempts")

    # if otp_record.otp != data.otp:
    if not bcrypt.checkpw(
    data.otp.encode(),
    otp_record.otp_hash.encode()
    ):
        otp_record.attempts += 1
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid OTP")

    otp_record.is_verified = True
    db.commit()

    return {"message": "OTP verified successfully"}


# reset password
@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):

    otp_record = db.query(EmailOTP).filter(
        EmailOTP.email == data.email,
        EmailOTP.is_verified == True
    ).first()

    if not otp_record:
        raise HTTPException(status_code=400, detail="OTP not verified")

    user = get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = get_password_hash(data.new_password)

    db.delete(otp_record)
    db.commit()

    return {"message": "Password reset successful"}
