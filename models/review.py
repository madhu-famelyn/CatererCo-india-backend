from database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    author_name = Column(String, nullable=False)
    target_name = Column(String, nullable=False)
    target_type = Column(String, default="caterer")  # caterer or customer
    rating = Column(Integer, default=5)
    content = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, approved, removed
    is_reported = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
