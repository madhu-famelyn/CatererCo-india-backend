from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.booking import Booking
from models.caterer import Caterer
from models.user import User
from models.notification import Notification
from schemas.booking import BookingOut, BookingCreate
from core.deps import get_current_user
from core.email import send_booking_email
import uuid

router = APIRouter(prefix="/bookings", tags=["bookings"])


def _enrich(b: Booking, db: Session) -> dict:
    caterer = db.query(Caterer).filter(Caterer.id == b.caterer_id).first()
    return {
        "id": b.id,
        "caterer_id": b.caterer_id,
        "caterer_name": caterer.name if caterer else b.caterer_id,
        "event": b.event,
        "date": b.event_date,
        "guests": b.guests,
        "total": b.total,
        "status": b.status.value if hasattr(b.status, "value") else b.status,
        "address": b.address,
        "emirate": b.emirate,
    }


@router.get("", response_model=List[BookingOut])
def list_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bookings = (
        db.query(Booking)
        .filter(Booking.customer_id == current_user.id)
        .order_by(Booking.created_at.desc())
        .all()
    )
    return [_enrich(b, db) for b in bookings]


@router.get("/{booking_id}")
def get_booking(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    b = db.query(Booking).filter(Booking.id == booking_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")
    return _enrich(b, db)


@router.post("", status_code=201)
def create_booking(
    data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking_id = f"BK-{str(uuid.uuid4())[:4].upper()}"
    booking = Booking(
        id=booking_id,
        customer_id=current_user.id,
        caterer_id=data.caterer_id,
        event=data.event,
        event_date=data.event_date,
        guests=data.guests,
        total=data.total,
        status="confirmed",
        address=data.address,
        emirate=data.emirate,
        notes=data.notes,
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    enriched_data = _enrich(booking, db)

    # Insert Real-Time Notification into Database
    notif = Notification(
        user_id=current_user.id,
        title="Booking Confirmed 🎉",
        body=f"Your booking {booking_id} for {enriched_data.get('caterer_name', 'Caterer')} is confirmed for {data.event_date}.",
        unread=True,
    )
    db.add(notif)
    db.commit()


    # 1. Send confirmation email to Customer
    if current_user.email:
        send_booking_email(
            to_email=current_user.email,
            recipient_name=current_user.first_name,
            booking_data=enriched_data,
            is_vendor=False
        )

    # 2. Send notification email to Vendor (caterer owner)
    caterer = db.query(Caterer).filter(Caterer.id == data.caterer_id).first()
    if caterer and caterer.owner_id:
        vendor_user = db.query(User).filter(User.id == caterer.owner_id).first()
        if vendor_user and vendor_user.email:
            send_booking_email(
                to_email=vendor_user.email,
                recipient_name=vendor_user.first_name,
                booking_data=enriched_data,
                is_vendor=True
            )

    return enriched_data


# Admin-facing: list all bookings across all caterers and customers
@router.get("/admin/all")
def list_admin_all_bookings(db: Session = Depends(get_db)):
    bookings = db.query(Booking).order_by(Booking.created_at.desc()).all()
    res = []
    for b in bookings:
        c = db.query(Caterer).filter(Caterer.id == b.caterer_id).first()
        u = db.query(User).filter(User.id == b.customer_id).first()
        res.append({
            "id": b.id,
            "customer": f"{u.first_name} {u.last_name}" if u else f"Customer #{b.customer_id}",
            "caterer": c.name if c else b.caterer_id,
            "eventType": b.event,
            "eventDate": b.event_date,
            "guests": b.guests,
            "amount": int(b.total),
            "status": b.status.value if hasattr(b.status, "value") else b.status,
            "address": b.address,
            "emirate": b.emirate,
        })
    return res


# Caterer-facing: list all bookings for this caterer
@router.get("/caterer/all")
def list_caterer_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Find caterer record owned by this user
    caterer = db.query(Caterer).filter(Caterer.owner_id == current_user.id).first()
    if not caterer:
        # If no caterer profile, return empty
        return []
    bookings = db.query(Booking).filter(Booking.caterer_id == caterer.id).all()
    return [_enrich(b, db) for b in bookings]


@router.delete("/{booking_id}")
def delete_booking(
    booking_id: str,
    db: Session = Depends(get_db),
):
    b = db.query(Booking).filter(Booking.id == booking_id).first()
    if b:
        db.delete(b)
        db.commit()
    return {"message": "Booking deleted successfully"}


