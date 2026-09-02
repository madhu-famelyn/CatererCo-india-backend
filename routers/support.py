from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.support import SupportTicket
from typing import List, Optional

router = APIRouter(prefix="/support", tags=["support"])


@router.get("/tickets")
def list_tickets(db: Session = Depends(get_db)):
    tickets = db.query(SupportTicket).order_by(SupportTicket.created_at.desc()).all()
    return [
        {
            "id": t.id,
            "subject": t.subject,
            "from": t.from_user,
            "type": t.user_type,
            "priority": t.priority,
            "assignee": t.assignee,
            "status": t.status,
            "createdAt": t.created_at.strftime("%Y-%m-%d") if t.created_at else "Recently",
        }
        for t in tickets
    ]


@router.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    t = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {
        "id": t.id,
        "subject": t.subject,
        "from": t.from_user,
        "type": t.user_type,
        "priority": t.priority,
        "assignee": t.assignee,
        "status": t.status,
        "createdAt": t.created_at.strftime("%Y-%m-%d") if t.created_at else "Recently",
        "messages": [
            {"sender": t.from_user, "role": t.user_type, "text": f"Inquiry regarding {t.subject}", "date": "2 hours ago"}
        ]
    }


@router.patch("/tickets/{ticket_id}/status")
def update_ticket_status(ticket_id: str, status: str, db: Session = Depends(get_db)):
    t = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Ticket not found")
    t.status = status
    db.commit()
    return {"message": f"Ticket status updated to {status}"}


@router.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: str, db: Session = Depends(get_db)):
    t = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if t:
        db.delete(t)
        db.commit()
    return {"message": "Ticket deleted successfully"}
