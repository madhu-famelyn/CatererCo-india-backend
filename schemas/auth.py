from pydantic import BaseModel, EmailStr
from typing import Optional


class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str
    role: str = "customer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class OtpVerifyRequest(BaseModel):
    email: EmailStr
    otp: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user: dict


class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    role: str
    is_verified: bool
    preferred_emirate: Optional[str]
    language: str

    class Config:
        from_attributes = True


class GoogleLoginRequest(BaseModel):
    id_token: str
    role: str = "customer"


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordWithOtpRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

