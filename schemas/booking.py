from pydantic import BaseModel
from typing import Optional


class BookingOut(BaseModel):
    id: str
    caterer_id: str
    caterer_name: Optional[str] = None
    event: str
    date: str
    guests: int
    total: float
    status: str
    address: Optional[str]
    emirate: Optional[str]

    class Config:
        from_attributes = True


class BookingCreate(BaseModel):
    caterer_id: str
    event: str
    event_date: str
    guests: int
    total: float
    address: Optional[str] = None
    emirate: Optional[str] = None
    notes: Optional[str] = None
