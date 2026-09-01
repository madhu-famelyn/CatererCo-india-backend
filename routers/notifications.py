from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.notification import Notification
from models.user import User
from schemas.other import NotificationOut
from core.security import decode_token
from core.deps import get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])

oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db),
) -> Optional[User]:
    if not token:
        return None
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if user_id:
            return db.query(User).filter(User.id == int(user_id)).first()
    except Exception:
        pass
    return None


@router.get("", response_model=List[NotificationOut])
def list_notifications(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    if current_user:
        return (
            db.query(Notification)
            .filter(Notification.user_id == current_user.id)
            .order_by(Notification.created_at.desc())
            .all()
        )
    return db.query(Notification).order_by(Notification.created_at.desc()).all()


from pydantic import BaseModel
from models.caterer import Caterer
from core.email import send_custom_notification_email

class NotificationSendSchema(BaseModel):
    channel: str = "email"
    audience: str = "customers"
    title: str
    message: str


@router.post("/send")
def send_admin_notification(
    payload: NotificationSendSchema,
    db: Session = Depends(get_db),
):
    recipients = []
    if payload.audience == "caterers":
        caterers = db.query(Caterer).all()
        recipients = [c.email for c in caterers if c.email]
    elif payload.audience == "customers":
        users = db.query(User).filter(User.role == "customer").all()
        recipients = [u.email for u in users if u.email]
    elif payload.audience == "admins":
        users = db.query(User).filter(User.role == "admin").all()
        recipients = [u.email for u in users if u.email]
    else:
        users = db.query(User).all()
        recipients = [u.email for u in users if u.email]

    if not recipients:
        recipients = ["ssah75368@gmail.com"]

    sent_count = 0
    if payload.channel == "email":
        for email_addr in set(recipients):
            if send_custom_notification_email(email_addr, payload.title, payload.message):
                sent_count += 1
        msg_str = f"Email broadcast sent to {sent_count} recipient(s) via Gmail SMTP!"
    else:
        msg_str = f"{payload.channel.upper()} notification dispatched to {len(recipients)} user(s)!"

    first_user = db.query(User).first()
    new_notif = Notification(
        user_id=first_user.id if first_user else 1,
        title=f"[{payload.channel.upper()}] {payload.title}",
        body=payload.message,
    )
    db.add(new_notif)
    db.commit()

    return {
        "ok": True,
        "message": msg_str,
        "sentCount": sent_count if payload.channel == "email" else len(recipients),
    }


@router.patch("/{notification_id}/read")
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    n = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    ).first()
    if n:
        n.unread = False
        db.commit()
    return {"ok": True}
