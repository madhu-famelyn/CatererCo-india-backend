from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime


class CatererOut(BaseModel):
    id: str
    name: str
    rating: float
    reviews: int
    location: str
    tags: List[str] = []
    starting_from: float
    cover: Optional[str] = None
    about: Optional[str] = None
    trade_license: Optional[str] = None
    vat_number: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emirate: Optional[str] = None
    certifications: List[str] = []
    documents: List[str] = []
    cuisine_types: List[str] = []
    is_verified: bool = False
    is_eco_friendly: bool = False
    eco_practices: List[str] = []
    iso_14001_certified: bool = False
    iso_14001_certificate: Optional[str] = None
    google_rating: Optional[float] = None
    google_reviews_count: Optional[int] = None
    google_place_id: Optional[str] = None
    google_review_url: Optional[str] = None
    years_in_business: Optional[int] = None
    orders_delivered: Optional[int] = None
    min_order_plates: Optional[int] = 0
    menu_items_count: Optional[int] = 0
    created_at: Optional[datetime] = None

    # Coerce NULL database values to empty lists for all JSON list fields
    @field_validator("tags", "certifications", "documents", "cuisine_types", "eco_practices", mode="before")
    @classmethod
    def none_to_list(cls, v):
        return v if v is not None else []

    class Config:
        from_attributes = True


class CatererCreate(BaseModel):
    company: str
    license: str
    vat: str
    contact: str
    email: str
    phone: str
    emirate: str
    address: str
    min_order_plates: Optional[int] = 0
    is_eco_friendly: Optional[bool] = False
    eco_practices: Optional[List[str]] = []
    iso_14001_certified: Optional[bool] = False
    iso_14001_certificate: Optional[str] = None


class CatererUpdate(BaseModel):
    name: Optional[str] = None
    about: Optional[str] = None
    address: Optional[str] = None
    emirate: Optional[str] = None
    tags: Optional[List[str]] = None
    cuisine_types: Optional[List[str]] = None
    cover: Optional[str] = None
    min_order_plates: Optional[int] = None
    is_eco_friendly: Optional[bool] = None
    eco_practices: Optional[List[str]] = None
    iso_14001_certified: Optional[bool] = None
    iso_14001_certificate: Optional[str] = None
    certifications: Optional[List[str]] = None
    documents: Optional[List[str]] = None
    google_rating: Optional[float] = None
    google_reviews_count: Optional[int] = None
    google_place_id: Optional[str] = None
    google_review_url: Optional[str] = None
    years_in_business: Optional[int] = None
    orders_delivered: Optional[int] = None
