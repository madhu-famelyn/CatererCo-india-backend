from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.event import Event
from models.user import User
from schemas.other import EventCreate
from core.deps import get_current_user

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", status_code=201)
def submit_event(
    data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = Event(
        customer_id=current_user.id,
        event_type=data.event_type,
        event_date=data.event_date,
        event_time=data.event_time,
        guest_count=data.guest_count,
        budget=data.budget,
        cuisines=data.cuisines,
        dietary=data.dietary,
        serving_styles=data.serving_styles,
        address=data.address,
        emirate=data.emirate,
        venue_type=data.venue_type,
        requirements=data.requirements,
        notes=data.notes,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return {"id": event.id, "message": "Event submitted successfully"}


@router.get("")
def list_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    events = db.query(Event).filter(Event.customer_id == current_user.id).all()
    return events
