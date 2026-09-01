from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.review import Review
from typing import List, Optional

router = APIRouter(prefix="/reviews", tags=["reviews"])


from pydantic import BaseModel


class ReviewCreate(BaseModel):
    author_name: Optional[str] = "Customer"
    target_name: str
    target_type: Optional[str] = "caterer"
    rating: int = 5
    content: str
    status: Optional[str] = "pending"


@router.get("")
def list_reviews(db: Session = Depends(get_db)):
    reviews = db.query(Review).order_by(Review.created_at.desc()).all()
    return [
        {
            "id": f"REV-{r.id}",
            "rawId": r.id,
            "author": r.author_name,
            "target": r.target_name,
            "targetType": r.target_type,
            "rating": r.rating,
            "content": r.content,
            "status": r.status,
            "reported": r.is_reported,
            "date": r.created_at.strftime("%Y-%m-%d") if r.created_at else "Recently",
        }
        for r in reviews
    ]


@router.post("", status_code=201)
def create_review(data: ReviewCreate, db: Session = Depends(get_db)):
    review = Review(
        author_name=data.author_name or "Customer",
        target_name=data.target_name,
        target_type=data.target_type or "caterer",
        rating=data.rating,
        content=data.content,
        status=data.status or "pending",
        is_reported=False,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return {
        "id": f"REV-{review.id}",
        "rawId": review.id,
        "author": review.author_name,
        "target": review.target_name,
        "targetType": review.target_type,
        "rating": review.rating,
        "content": review.content,
        "status": review.status,
        "reported": review.is_reported,
        "date": review.created_at.strftime("%Y-%m-%d") if review.created_at else "Recently",
    }


@router.patch("/{review_id}/status")
def update_review_status(review_id: int, status: str, db: Session = Depends(get_db)):
    r = db.query(Review).filter(Review.id == review_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Review not found")
    r.status = status
    db.commit()
    return {"ok": True, "message": f"Review status updated to {status}"}


@router.delete("/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db)):
    r = db.query(Review).filter(Review.id == review_id).first()
    if r:
        db.delete(r)
        db.commit()
    return {"ok": True, "message": "Review deleted successfully"}
