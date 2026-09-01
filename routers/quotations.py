from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.quotation import Quotation, QuotationStatus
from models.caterer import Caterer
from models.user import User
from schemas.quotation import QuotationOut, QuotationCreate, QuotationUpdate
from core.deps import get_current_user
import uuid

router = APIRouter(prefix="/quotations", tags=["quotations"])


def _enrich(q: Quotation, db: Session) -> dict:
    caterer = db.query(Caterer).filter(Caterer.id == q.caterer_id).first()
    return {
        "id": q.id,
        "caterer_id": q.caterer_id,
        "caterer_name": caterer.name if caterer else q.caterer_id,
        "event": q.event,
        "guests": q.guests,
        "total": q.total,
        "status": q.status.value if hasattr(q.status, "value") else q.status,
        "valid_till": q.valid_till,
    }


@router.get("", response_model=List[QuotationOut])
def list_quotations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status: Optional[str] = Query(None),
):
    query = db.query(Quotation)
    if current_user.role.value == "customer":
        query = query.filter(Quotation.customer_id == current_user.id)
    else:
        # Caterer sees their own quotations
        from sqlalchemy import func
        caterer = db.query(Caterer).filter(
            (Caterer.owner_id == current_user.id) | (func.lower(Caterer.email) == current_user.email.lower())
        ).first()
        if caterer:
            query = query.filter(Quotation.caterer_id == caterer.id)
        else:
            return []
    if status:
        query = query.filter(Quotation.status == status)
    quotations = query.all()
    return [_enrich(q, db) for q in quotations]


@router.get("/{quotation_id}")
def get_quotation(
    quotation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return _enrich(q, db)


@router.post("", status_code=201)
def create_quotation(
    data: QuotationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    qid = f"QT-{str(uuid.uuid4())[:4].upper()}"
    quotation = Quotation(
        id=qid,
        customer_id=current_user.id,
        caterer_id=data.caterer_id,
        event=data.event,
        guests=data.guests,
        total=data.total,
        valid_till=data.valid_till,
        notes=data.notes,
    )
    db.add(quotation)
    db.commit()
    db.refresh(quotation)
    return _enrich(quotation, db)


@router.patch("/{quotation_id}/approve")
def approve_quotation(
    quotation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Quotation not found")
    q.status = QuotationStatus.approved
    db.commit()
    return _enrich(q, db)


@router.patch("/{quotation_id}/reject")
def reject_quotation(
    quotation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Quotation not found")
    q.status = QuotationStatus.rejected
    db.commit()
    return _enrich(q, db)


@router.patch("/{quotation_id}")
def update_quotation(
    quotation_id: str,
    data: QuotationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Quotation not found")
    if data.total is not None:
        q.total = data.total
    if data.notes is not None:
        q.notes = data.notes
    db.commit()
    return _enrich(q, db)


@router.delete("/{quotation_id}")
def delete_quotation(
    quotation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if q:
        db.delete(q)
        db.commit()
    return {"message": "Quotation deleted successfully"}


