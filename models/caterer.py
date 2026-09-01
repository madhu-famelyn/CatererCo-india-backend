from database import Base
from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime


class Caterer(Base):
    __tablename__ = "caterers"

    id = Column(String, primary_key=True, index=True)  # e.g. "c1"
    name = Column(String, nullable=False)
    rating = Column(Float, default=0.0)
    reviews = Column(Integer, default=0)
    location = Column(String, nullable=False)
    tags = Column(JSON, default=[])  # ["Halal", "Emirati", ...]
    starting_from = Column(Float, default=0)
    cover = Column(String, nullable=True)
    about = Column(String, nullable=True)
    trade_license = Column(String, nullable=True)
    vat_number = Column(String, nullable=True)
    contact_person = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    emirate = Column(String, nullable=True)
    # Staff counts
    chefs = Column(Integer, default=0)
    waiters = Column(Integer, default=0)
    multilingual_staff = Column(Integer, default=0)
    # Certifications and uploaded documents stored as JSON lists
    certifications = Column(JSON, default=[])
    documents = Column(JSON, default=[])
    # Cuisine specialisations selected during registration (e.g. ["Indian", "Emirati"])
    cuisine_types = Column(JSON, default=[])
    gallery = Column(JSON, default=[])
    is_verified = Column(Boolean, default=False)
    # Eco-friendly & ISO 14001 sustainability
    is_eco_friendly = Column(Boolean, default=False)
    eco_practices = Column(JSON, default=[])  # ["iso_14001", "biodegradable", "zero_waste", "organic"]
    iso_14001_certified = Column(Boolean, default=False)
    iso_14001_certificate = Column(String, nullable=True)
    # Real Google reviews & Credibility
    google_rating = Column(Float, nullable=True)
    google_reviews_count = Column(Integer, nullable=True)
    google_place_id = Column(String, nullable=True)
    google_review_url = Column(String, nullable=True)
    years_in_business = Column(Integer, nullable=True)
    orders_delivered = Column(Integer, nullable=True)
    # Minimum order plates / guest count requirement (0 = no minimum)
    min_order_plates = Column(Integer, default=0)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    # AI-generated catering packages saved by the caterer
    packages = Column(JSON, default=[])

    # Relationships
    menu_items = relationship("MenuItem", back_populates="caterer")
    bookings = relationship("Booking", back_populates="caterer")
    quotations = relationship("Quotation", back_populates="caterer")

