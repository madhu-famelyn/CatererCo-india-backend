from database import Base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum


class QuotationStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class Quotation(Base):
    __tablename__ = "quotations"

    id = Column(String, primary_key=True, index=True)  # e.g. "QT-2201"
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    caterer_id = Column(String, ForeignKey("caterers.id"), nullable=False)
    event = Column(String, nullable=False)
    guests = Column(Integer, default=0)
    total = Column(Float, nullable=False)
    status = Column(Enum(QuotationStatus), default=QuotationStatus.pending)
    valid_till = Column(String, nullable=True)   # ISO date string
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("User", back_populates="quotations", foreign_keys=[customer_id])
    caterer = relationship("Caterer", back_populates="quotations")
