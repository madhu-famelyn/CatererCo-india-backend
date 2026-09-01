from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.auth import (
    RegisterRequest,
    LoginRequest,
    OtpVerifyRequest,
    TokenResponse,
    GoogleLoginRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordWithOtpRequest,
)
from core.security import hash_password, verify_password, create_access_token
from core.email import send_otp_email, send_password_change_email, send_password_reset_otp_email
from core.deps import get_current_user
import random
import os
import urllib.request
import json

router = APIRouter(prefix="/auth", tags=["auth"])

MOCK_OTP = "123456"


def verify_google_token(id_token: str):
    url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "FastAPI-OAuth"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            if "error" in data:
                return None
            return data
    except Exception:
        return None



@router.post("/register", status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    clean_email = data.email.strip().lower()
    existing = db.query(User).filter(func.lower(User.email) == clean_email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Generate random 6-digit OTP if SMTP is configured; fallback to mock OTP otherwise
    smtp_enabled = os.getenv("SMTP_USERNAME") is not None
    otp_code = str(random.randint(100000, 999999)) if smtp_enabled else MOCK_OTP

    user = User(
        first_name=data.first_name,
        last_name=data.last_name,
        email=clean_email,
        phone=data.phone,
        hashed_password=hash_password(data.password),
        role=data.role,
        is_verified=False,
        otp_code=otp_code,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    if smtp_enabled:
        send_otp_email(user.email, otp_code)

    return {"message": "Registration successful. OTP sent.", "email": user.email}


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    from models.caterer import Caterer
    from models.user import UserRole

    clean_email = data.email.strip().lower()
    user = db.query(User).filter(func.lower(User.email) == clean_email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    caterer = db.query(Caterer).filter((Caterer.owner_id == user.id) | (func.lower(Caterer.email) == clean_email)).first()
    if caterer:
        if user.role != UserRole.caterer:
            user.role = UserRole.caterer
        if not caterer.owner_id:
            caterer.owner_id = user.id
        db.commit()

        if not caterer.is_verified:
            raise HTTPException(
                status_code=403,
                detail="Your caterer application is pending admin approval. You can log in once approved by admin."
            )

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role.value,
        "user": {
            "id": user.id,
            "name": f"{user.first_name} {user.last_name}",
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "caterer_id": caterer.id if caterer else None,
        },
    }


@router.post("/otp-verify")
def verify_otp(data: OtpVerifyRequest, db: Session = Depends(get_db)):
    clean_email = data.email.strip().lower()
    user = db.query(User).filter(func.lower(User.email) == clean_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if data.otp != user.otp_code and data.otp != MOCK_OTP:
        raise HTTPException(status_code=400, detail="Invalid OTP code")
    user.is_verified = True
    user.otp_code = None
    db.commit()
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role.value,
        "user": {
            "id": user.id,
            "name": f"{user.first_name} {user.last_name}",
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
    }


@router.post("/resend-otp")
def resend_otp(email: str, db: Session = Depends(get_db)):
    clean_email = email.strip().lower()
    user = db.query(User).filter(func.lower(User.email) == clean_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    smtp_enabled = os.getenv("SMTP_USERNAME") is not None
    otp_code = str(random.randint(100000, 999999)) if smtp_enabled else MOCK_OTP
    user.otp_code = otp_code
    db.commit()

    if smtp_enabled:
        send_otp_email(user.email, otp_code)

    return {"message": "OTP resent"}


@router.post("/google", response_model=TokenResponse)
def google_login(data: GoogleLoginRequest, db: Session = Depends(get_db)):
    payload = verify_google_token(data.id_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google credentials/token",
        )

    # Check client ID match if configured in environment
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    if google_client_id and payload.get("aud") != google_client_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token audience mismatch",
        )

    email = payload.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address not provided by Google account",
        )

    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Create a new user account if they don't exist
        first_name = payload.get("given_name", "Google")
        last_name = payload.get("family_name", "User")

        # Determine roles based on parameter
        from models.user import UserRole

        try:
            role_enum = UserRole(data.role)
        except ValueError:
            role_enum = UserRole.customer

        # Generate a random password since OAuth users bypass password login
        temp_pass = str(random.randint(10000000, 99999999))

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            hashed_password=hash_password(temp_pass),
            role=role_enum,
            is_verified=True,
            otp_code=None,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Automatically check if user email matches any caterer application profile
    from models.caterer import Caterer
    from sqlalchemy import func
    caterer = db.query(Caterer).filter(
        (Caterer.owner_id == user.id) | (func.lower(Caterer.email) == email.lower())
    ).first()
    if caterer:
        if user.role != UserRole.caterer:
            user.role = UserRole.caterer
        if not caterer.owner_id:
            caterer.owner_id = user.id
        db.commit()

    if not user.is_verified:
        user.is_verified = True
        db.commit()

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role.value,
        "user": {
            "id": user.id,
            "name": f"{user.first_name} {user.last_name}",
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
    }


@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    current_user.hashed_password = hash_password(data.new_password)
    db.commit()

    # Send password change notification email using EMAIL_FROM
    send_password_change_email(current_user.email, current_user.first_name)

    return {"message": "Password changed successfully"}


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    clean_email = data.email.strip().lower()
    user = db.query(User).filter(func.lower(User.email) == clean_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User with this email not found")

    # Generate 6-digit OTP
    otp_code = str(random.randint(100000, 999999))
    user.otp_code = otp_code
    db.commit()

    # Send reset OTP email via SMTP
    sent = send_password_reset_otp_email(user.email, otp_code, user.first_name)

    return {
        "message": "Password reset OTP sent to your email",
        "email": user.email,
        "sent": sent,
    }


@router.post("/reset-password")
def reset_password(data: ResetPasswordWithOtpRequest, db: Session = Depends(get_db)):
    clean_email = data.email.strip().lower()
    user = db.query(User).filter(func.lower(User.email) == clean_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.otp_code or (data.otp != user.otp_code and data.otp != MOCK_OTP):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP code")

    user.hashed_password = hash_password(data.new_password)
    user.otp_code = None
    db.commit()

    # Send confirmation email
    send_password_change_email(user.email, user.first_name)

    return {"message": "Password reset successfully. You can now login."}

