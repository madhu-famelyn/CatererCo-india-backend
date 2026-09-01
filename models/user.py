from database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum


class UserRole(str, enum.Enum):
    customer = "customer"
    caterer = "caterer"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.customer)
    is_verified = Column(Boolean, default=False)
    otp_code = Column(String, nullable=True)
    preferred_emirate = Column(String, nullable=True)
    language = Column(String, default="English")
    permissions = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    bookings = relationship("Booking", back_populates="customer", foreign_keys="Booking.customer_id")
    quotations = relationship("Quotation", back_populates="customer", foreign_keys="Quotation.customer_id")
    notifications = relationship("Notification", back_populates="user")
