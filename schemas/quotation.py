from pydantic import BaseModel
from typing import Optional


class QuotationOut(BaseModel):
    id: str
    caterer_id: str
    caterer_name: Optional[str] = None
    event: str
    guests: int
    total: float
    status: str
    valid_till: Optional[str]

    class Config:
        from_attributes = True


class QuotationCreate(BaseModel):
    caterer_id: str
    event: str
    guests: int
    total: float
    valid_till: Optional[str] = None
    notes: Optional[str] = None


class QuotationUpdate(BaseModel):
    total: Optional[float] = None
    notes: Optional[str] = None
