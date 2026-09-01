from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt
from database import get_db
from typing import Optional
from models.user import User
from core.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def get_current_user_optional(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    if not token:
        return None
    try:
        payload = decode_token(token)
        sub = payload.get("sub")
        if not sub:
            return None
        from sqlalchemy import func
        user = None
        if str(sub).isdigit():
            user = db.query(User).filter(User.id == int(sub)).first()
        if not user:
            user = db.query(User).filter(func.lower(User.email) == str(sub).lower()).first()
        return user
    except Exception:
        return None


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    try:
        payload = decode_token(token)
        sub = payload.get("sub")
        if not sub:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    from sqlalchemy import func
    user = None
    if str(sub).isdigit():
        user = db.query(User).filter(User.id == int(sub)).first()
    if not user:
        user = db.query(User).filter(func.lower(User.email) == str(sub).lower()).first()

    if user is None:
        raise credentials_exception
    return user


def get_current_caterer(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role.value != "caterer":
        raise HTTPException(status_code=403, detail="Caterer access required")
    return current_user
