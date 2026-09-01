from database import Base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(String, primary_key=True, index=True)
    caterer_id = Column(String, ForeignKey("caterers.id"), nullable=False)
    category = Column(String, nullable=False)  # starters, mains, desserts, beverages
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    is_vegetarian = Column(Boolean, default=False)
    is_popular = Column(Boolean, default=False)
    is_halal = Column(Boolean, default=True)
    is_spicy = Column(Boolean, default=False)
    description = Column(String, nullable=True)
    cuisine = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    caterer = relationship("Caterer", back_populates="menu_items")
