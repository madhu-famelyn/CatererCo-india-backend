from database import Base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(String, primary_key=True, index=True)
    subject = Column(String, nullable=False)
    from_user = Column(String, nullable=False)
    user_type = Column(String, default="customer")
    priority = Column(String, default="medium")
    assignee = Column(String, default="Unassigned")
    status = Column(String, default="open")
    created_at = Column(DateTime, default=datetime.utcnow)
