from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.auth import UserOut
from core.deps import get_current_user
from typing import List

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
@router.get("/")
def list_users(role: str = None, db: Session = Depends(get_db)):
    from models.booking import Booking
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    users = query.all()
    res = []
    for u in users:
        u_bookings = db.query(Booking).filter(Booking.customer_id == u.id).all()
        user_role = u.role.value if hasattr(u.role, "value") else u.role
        raw_perms = u.permissions.split(", ") if u.permissions else (
            ["Caterers", "Bookings", "Payments", "Support"] if user_role == "admin" else []
        )
        res.append({
            "id": u.id,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "email": u.email,
            "role": user_role,
            "permissions": raw_perms,
            "is_verified": u.is_verified,
            "bookings_count": len(u_bookings),
            "total_spent": sum(b.total for b in u_bookings if hasattr(b, 'status') and b.status and getattr(b.status, 'value', b.status) in ("confirmed", "completed")),
        })
    return res



from pydantic import BaseModel, EmailStr
from core.email import send_admin_invite_email
from models.user import User, UserRole

class InviteAdminSchema(BaseModel):
    name: str
    email: EmailStr
    role: str = "Admin"
    permissions: List[str] = []

class UpdatePermissionsSchema(BaseModel):
    permissions: List[str] = []

@router.post("/invite-admin")
def invite_admin(payload: InviteAdminSchema, db: Session = Depends(get_db)):
    perms_str = ", ".join(payload.permissions) if payload.permissions else "Full Access"
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        existing.role = UserRole.admin
        existing.permissions = perms_str
        db.commit()
    else:
        parts = payload.name.strip().split(" ", 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""
        new_user = User(
            email=payload.email,
            first_name=first_name,
            last_name=last_name,
            role=UserRole.admin,
            permissions=perms_str,
            is_verified=True,
            hashed_password="admin_invited_account",
        )
        db.add(new_user)
        db.commit()

    send_admin_invite_email(payload.email, payload.name, payload.role, payload.permissions)

    return {
        "ok": True,
        "message": f"Invitation email sent to {payload.email} with access permissions!",
    }


def _get_user_by_id_or_str(user_id_input: str, db: Session):
    s = str(user_id_input).strip()
    # Try direct numeric ID first
    try:
        numeric_id = int(s)
        u = db.query(User).filter(User.id == numeric_id).first()
        if u:
            return u
    except ValueError:
        pass

    # Try stripping CU- prefix if passed
    if s.lower().startswith("cu-"):
        clean_s = s[3:]
        try:
            numeric_id = int(clean_s)
            u = db.query(User).filter(User.id == numeric_id).first()
            if u:
                return u
        except ValueError:
            pass

    # Fallback to customer index mapping or email
    all_users = db.query(User).all()
    if s.lower().startswith("cu-"):
        try:
            idx = int(s[3:]) - 1
            customers = [usr for usr in all_users if (usr.role.value if hasattr(usr.role, "value") else usr.role) == "customer"]
            if 0 <= idx < len(customers):
                return customers[idx]
        except ValueError:
            pass

    return db.query(User).filter(User.email == user_id_input).first()


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}")
def get_user_by_id(user_id: str, db: Session = Depends(get_db)):
    from models.booking import Booking
    u = _get_user_by_id_or_str(user_id, db)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    
    u_bookings = db.query(Booking).filter(Booking.customer_id == u.id).all()
    user_role = u.role.value if hasattr(u.role, "value") else u.role
    raw_perms = u.permissions.split(", ") if u.permissions else (
        ["Caterers", "Bookings", "Payments", "Support"] if user_role == "admin" else []
    )
    return {
        "id": u.id,
        "first_name": u.first_name,
        "last_name": u.last_name,
        "email": u.email,
        "phone": u.phone,
        "role": user_role,
        "permissions": raw_perms,
        "is_verified": u.is_verified,
        "preferred_emirate": u.preferred_emirate,
        "language": u.language,
        "created_at": u.created_at,
        "bookings_count": len(u_bookings),
        "total_spent": sum(b.total for b in u_bookings if hasattr(b, 'status') and b.status and getattr(b.status, 'value', b.status) in ("confirmed", "completed")),
    }


@router.patch("/{user_id}/permissions")
def update_user_permissions(user_id: str, payload: UpdatePermissionsSchema, db: Session = Depends(get_db)):
    u = _get_user_by_id_or_str(user_id, db)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    u.permissions = ", ".join(payload.permissions)
    db.commit()
    return {"ok": True, "message": "Access permissions updated successfully"}


@router.delete("/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    from models.booking import Booking
    from models.quotation import Quotation
    from models.notification import Notification
    from models.caterer import Caterer
    from models.menu import MenuItem

    u = _get_user_by_id_or_str(user_id, db)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")

    user_numeric_id = u.id
    try:
        # Delete dependent child records
        db.query(Booking).filter(Booking.customer_id == user_numeric_id).delete(synchronize_session=False)
        db.query(Quotation).filter(Quotation.customer_id == user_numeric_id).delete(synchronize_session=False)
        db.query(Notification).filter(Notification.user_id == user_numeric_id).delete(synchronize_session=False)

        # Delete associated caterer profiles owned by this user or matching email
        caterers = db.query(Caterer).filter((Caterer.owner_id == user_numeric_id) | (Caterer.email == u.email)).all()
        for cat in caterers:
            db.query(Booking).filter(Booking.caterer_id == cat.id).delete(synchronize_session=False)
            db.query(Quotation).filter(Quotation.caterer_id == cat.id).delete(synchronize_session=False)
            db.query(MenuItem).filter(MenuItem.caterer_id == cat.id).delete(synchronize_session=False)
            db.delete(cat)

        db.flush()
        db.delete(u)
        db.commit()
        return {"message": "User deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")
