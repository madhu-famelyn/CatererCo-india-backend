from database import Base
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_type = Column(String, nullable=False)
    event_date = Column(String, nullable=False)
    event_time = Column(String, nullable=True)
    guest_count = Column(Integer, default=100)
    budget = Column(Float, default=0)
    cuisines = Column(JSON, default=[])
    dietary = Column(String, default="mixed")
    serving_styles = Column(JSON, default=[])
    address = Column(String, nullable=True)
    emirate = Column(String, nullable=True)
    venue_type = Column(String, nullable=True)
    requirements = Column(JSON, default={})
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
