from pydantic import BaseModel
from typing import Optional


class MenuItemOut(BaseModel):
    id: str
    caterer_id: str
    category: str
    name: str
    price: float
    is_vegetarian: bool
    is_popular: bool
    is_halal: bool = True
    is_spicy: bool = False
    description: Optional[str] = None
    cuisine: Optional[str] = None

    class Config:
        from_attributes = True


class MenuItemCreate(BaseModel):
    category: str
    name: str
    price: float
    is_vegetarian: bool = False
    is_popular: bool = False
    is_halal: bool = True
    is_spicy: bool = False
    description: Optional[str] = None
    cuisine: Optional[str] = None


class NotificationOut(BaseModel):
    id: int
    title: str
    body: Optional[str]
    time_label: Optional[str]
    unread: bool

    class Config:
        from_attributes = True


class EventCreate(BaseModel):
    event_type: str
    event_date: str
    event_time: Optional[str] = None
    guest_count: int = 100
    budget: float = 0
    cuisines: list = []
    dietary: str = "mixed"
    serving_styles: list = []
    address: Optional[str] = None
    emirate: Optional[str] = None
    venue_type: Optional[str] = None
    requirements: dict = {}
    notes: Optional[str] = None
