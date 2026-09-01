from database import Base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum


class BookingStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in-progress"
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(String, primary_key=True, index=True)  # e.g. "BK-1042"
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    caterer_id = Column(String, ForeignKey("caterers.id"), nullable=False)
    event = Column(String, nullable=False)
    event_date = Column(String, nullable=False)   # ISO date string
    guests = Column(Integer, nullable=False)
    total = Column(Float, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.pending)
    address = Column(String, nullable=True)
    emirate = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("User", back_populates="bookings", foreign_keys=[customer_id])
    caterer = relationship("Caterer", back_populates="bookings")
