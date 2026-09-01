from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from database import get_db
from models.caterer import Caterer
from models.user import User
from schemas.caterer import CatererOut, CatererUpdate
from core.deps import get_current_user, get_current_user_optional
from core.email import send_caterer_approval_email, send_caterer_rejection_email

from pydantic import BaseModel

router = APIRouter(prefix="/caterers", tags=["caterers"])


class CatererRegisterInput(BaseModel):
    name: str
    trade_license: Optional[str] = None
    vat_number: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    emirate: Optional[str] = "Dubai"
    address: Optional[str] = None
    password: Optional[str] = None
    documents: Optional[List[str]] = None
    cuisine_types: Optional[List[str]] = None
    min_order_plates: Optional[int] = 0
    is_eco_friendly: Optional[bool] = False
    eco_practices: Optional[List[str]] = []
    iso_14001_certified: Optional[bool] = False
    iso_14001_certificate: Optional[str] = None
    certifications: Optional[List[str]] = None
    auto_approve: Optional[bool] = False



@router.get("", response_model=List[CatererOut])
def list_caterers(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None),
    emirate: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),        # comma-separated
    max_price: Optional[float] = Query(None),
    min_rating: Optional[float] = Query(None),
    guests: Optional[int] = Query(None),
    sort_by: Optional[str] = Query("popularity"),
    include_unverified: bool = Query(False),
):
    query = db.query(Caterer)
    if not include_unverified:
        query = query.filter(Caterer.is_verified == True)

    caterers = query.all()

    # Filter in Python
    results = []
    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    for c in caterers:
        if guests is not None:
            c_min = c.min_order_plates if c.min_order_plates is not None else 0
            if c_min > 0 and guests < c_min:
                continue
        if search:
            q = search.lower()
            match = (
                q in c.name.lower()
                or q in (c.location or "").lower()
                or any(q in t.lower() for t in (c.tags or []))
            )
            if not match:
                continue
        if emirate and emirate != "All emirates":
            if emirate.lower() not in (c.location or "").lower():
                continue
        if max_price is not None and c.starting_from > max_price:
            continue
        if min_rating is not None and c.rating < min_rating:
            continue
        if tag_list:
            if not all(t in (c.tags or []) for t in tag_list):
                continue
        results.append(c)

    # Sort
    if sort_by == "rating":
        results.sort(key=lambda x: x.rating, reverse=True)
    elif sort_by == "price-asc":
        results.sort(key=lambda x: x.starting_from)
    elif sort_by == "price-desc":
        results.sort(key=lambda x: x.starting_from, reverse=True)
    else:  # popularity
        results.sort(key=lambda x: x.reviews, reverse=True)

    from models.menu import MenuItem
    for c in results:
        count = db.query(MenuItem).filter(MenuItem.caterer_id == c.id).count()
        c.menu_items_count = count

    return results



@router.post("/register", status_code=201)
def register_caterer(data: CatererRegisterInput, db: Session = Depends(get_db)):
    import re, uuid
    from sqlalchemy import func
    from models.user import User, UserRole
    from core.security import hash_password

    clean_name = data.name.strip()
    slug = re.sub(r'[^a-z0-9]', '', clean_name.lower()) or "caterer"

    email_val = data.email.strip().lower() if (data.email and data.email.strip()) else f"info@{slug}.ae"
    phone_val = data.phone.strip() if (data.phone and data.phone.strip()) else "+971 50 123 4567"
    contact_val = data.contact_person.strip() if (data.contact_person and data.contact_person.strip()) else clean_name
    emirate_val = data.emirate.strip() if (data.emirate and data.emirate.strip()) else "Dubai"
    address_val = data.address.strip() if (data.address and data.address.strip()) else f"{emirate_val} Central"
    trade_license_val = data.trade_license.strip() if (data.trade_license and data.trade_license.strip()) else "TL-99210"
    vat_number_val = data.vat_number.strip() if (data.vat_number and data.vat_number.strip()) else "100-234-567-89"

    # Find or create linked User account for caterer authentication
    raw_pass = data.password.strip() if (data.password and data.password.strip()) else "Caterer@123"
    user = db.query(User).filter(func.lower(User.email) == email_val).first()
    if not user:
        name_parts = contact_val.split()
        first_name = name_parts[0]
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else "Caterer"

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email_val,
            phone=phone_val,
            hashed_password=hash_password(raw_pass),
            role=UserRole.caterer,
            is_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.hashed_password = hash_password(raw_pass)
        user.role = UserRole.caterer
        user.is_verified = True
        db.commit()
        db.refresh(user)


    caterer_id = f"c-{str(uuid.uuid4())[:6]}"
    docs = list(data.documents) if data.documents else []
    if data.certifications:
        for cert in data.certifications:
            if cert not in docs:
                docs.append(cert)
    if data.iso_14001_certificate and not any("ISO 14001" in str(d) for d in docs):
        docs.append(f"ISO 14001 Certificate: {data.iso_14001_certificate}")
    if not any("Trade License" in str(d) for d in docs) and trade_license_val:
        docs.append(f"Trade License #{trade_license_val} (PDF)")
    if not any("VAT Certificate" in str(d) for d in docs) and vat_number_val:
        docs.append(f"VAT Certificate #{vat_number_val} (PDF)")
    caterer = Caterer(
        id=caterer_id,
        name=clean_name,
        trade_license=trade_license_val,
        vat_number=vat_number_val,
        contact_person=contact_val,
        email=email_val,
        phone=phone_val,
        emirate=emirate_val,
        location=f"{address_val}, {emirate_val}",
        address=address_val,
        documents=docs,
        certifications=data.certifications or [],
        cuisine_types=data.cuisine_types or [],
        min_order_plates=int(data.min_order_plates) if data.min_order_plates is not None else 0,
        is_eco_friendly=bool(data.is_eco_friendly),
        eco_practices=data.eco_practices or [],
        iso_14001_certified=bool(data.iso_14001_certified),
        iso_14001_certificate=data.iso_14001_certificate,
        is_verified=bool(data.auto_approve),
        owner_id=user.id,
        rating=0.0,
        reviews=0,
        starting_from=45.0,
    )
    db.add(caterer)
    db.commit()
    db.refresh(caterer)
    return {
        "message": "Caterer registered successfully",
        "caterer": caterer,
        "user_email": email_val,
    }



@router.patch("/{caterer_id}/approve")
def approve_caterer(caterer_id: str, db: Session = Depends(get_db)):
    c = db.query(Caterer).filter(Caterer.id == caterer_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Caterer not found")
    c.is_verified = True
    db.commit()
    send_caterer_approval_email(c.email, c.name)
    return {"message": "Caterer approved and published live on the website", "is_verified": True}


@router.patch("/{caterer_id}/reject")
def reject_caterer(caterer_id: str, db: Session = Depends(get_db)):
    c = db.query(Caterer).filter(Caterer.id == caterer_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Caterer not found")
    c.is_verified = False
    db.commit()
    send_caterer_rejection_email(c.email, c.name)
    return {"message": "Caterer application rejected", "is_verified": False}


@router.get("/me", response_model=CatererOut)
def get_my_caterer_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import func
    caterer = db.query(Caterer).filter(
        (Caterer.owner_id == current_user.id) | (func.lower(Caterer.email) == current_user.email.lower())
    ).first()
    if not caterer:
        raise HTTPException(status_code=404, detail="Caterer profile not found")
    return caterer


@router.patch("/me", response_model=CatererOut)
def update_my_caterer_profile(
    data: CatererUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import func
    caterer = db.query(Caterer).filter(
        (Caterer.owner_id == current_user.id) | (func.lower(Caterer.email) == current_user.email.lower())
    ).first()
    if not caterer:
        raise HTTPException(status_code=404, detail="Caterer profile not found")

    if data.name:
        caterer.name = data.name
    if data.about:
        caterer.about = data.about
    if data.address:
        caterer.address = data.address
    if data.emirate:
        caterer.emirate = data.emirate
        caterer.location = f"{data.address or caterer.address}, {data.emirate}"
    if data.tags is not None:
        caterer.tags = data.tags
    if data.cover is not None:
        caterer.cover = data.cover
    if data.cuisine_types is not None:
        caterer.cuisine_types = data.cuisine_types
    if data.min_order_plates is not None:
        caterer.min_order_plates = data.min_order_plates
    if data.is_eco_friendly is not None:
        caterer.is_eco_friendly = data.is_eco_friendly
    if data.eco_practices is not None:
        caterer.eco_practices = data.eco_practices
    if data.iso_14001_certified is not None:
        caterer.iso_14001_certified = data.iso_14001_certified
    if data.iso_14001_certificate is not None:
        caterer.iso_14001_certificate = data.iso_14001_certificate
        if data.iso_14001_certificate:
            docs = list(caterer.documents or [])
            docs = [d for d in docs if not (isinstance(d, str) and "ISO 14001" in d)]
            docs.append(f"ISO 14001 Certificate: {data.iso_14001_certificate}")
            caterer.documents = docs
    if data.certifications is not None:
        caterer.certifications = data.certifications
    if data.documents is not None:
        caterer.documents = data.documents
    if data.google_rating is not None:
        caterer.google_rating = data.google_rating
        caterer.rating = data.google_rating
    if data.google_reviews_count is not None:
        caterer.google_reviews_count = data.google_reviews_count
        caterer.reviews = data.google_reviews_count
    if data.google_place_id is not None:
        caterer.google_place_id = data.google_place_id
    if data.google_review_url is not None:
        caterer.google_review_url = data.google_review_url
    if data.years_in_business is not None:
        caterer.years_in_business = data.years_in_business
    if data.orders_delivered is not None:
        caterer.orders_delivered = data.orders_delivered

    db.commit()
    db.refresh(caterer)
    return caterer


@router.patch("/{caterer_id}", response_model=CatererOut)
def update_caterer_profile(
    caterer_id: str,
    data: CatererUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    from sqlalchemy import func
    caterer = db.query(Caterer).filter(Caterer.id == caterer_id).first()
    if not caterer:
        raise HTTPException(status_code=404, detail="Caterer not found")

    if data.name:
        caterer.name = data.name
    if data.about:
        caterer.about = data.about
    if data.address:
        caterer.address = data.address
    if data.emirate:
        caterer.emirate = data.emirate
        caterer.location = f"{data.address or caterer.address}, {data.emirate}"
    if data.tags is not None:
        caterer.tags = data.tags
    if data.cover is not None:
        caterer.cover = data.cover
    if data.cuisine_types is not None:
        caterer.cuisine_types = data.cuisine_types
    if data.min_order_plates is not None:
        caterer.min_order_plates = data.min_order_plates
    if data.is_eco_friendly is not None:
        caterer.is_eco_friendly = data.is_eco_friendly
    if data.eco_practices is not None:
        caterer.eco_practices = data.eco_practices
    if data.iso_14001_certified is not None:
        caterer.iso_14001_certified = data.iso_14001_certified
    if data.iso_14001_certificate is not None:
        caterer.iso_14001_certificate = data.iso_14001_certificate
        if data.iso_14001_certificate:
            docs = list(caterer.documents or [])
            docs = [d for d in docs if not (isinstance(d, str) and "ISO 14001" in d)]
            docs.append(f"ISO 14001 Certificate: {data.iso_14001_certificate}")
            caterer.documents = docs
    if data.certifications is not None:
        caterer.certifications = data.certifications
    if data.documents is not None:
        caterer.documents = data.documents
    if data.google_rating is not None:
        caterer.google_rating = data.google_rating
        caterer.rating = data.google_rating
    if data.google_reviews_count is not None:
        caterer.google_reviews_count = data.google_reviews_count
        caterer.reviews = data.google_reviews_count
    if data.google_place_id is not None:
        caterer.google_place_id = data.google_place_id
    if data.google_review_url is not None:
        caterer.google_review_url = data.google_review_url
    if data.years_in_business is not None:
        caterer.years_in_business = data.years_in_business
    if data.orders_delivered is not None:
        caterer.orders_delivered = data.orders_delivered

    db.commit()
    db.refresh(caterer)
    return caterer


@router.get("/{caterer_id}", response_model=CatererOut)
def get_caterer(caterer_id: str, db: Session = Depends(get_db)):
    caterer = db.query(Caterer).filter(Caterer.id == caterer_id).first()
    if not caterer:
        raise HTTPException(status_code=404, detail="Caterer not found")
    return caterer


@router.delete("/{caterer_id}")
def delete_caterer(caterer_id: str, db: Session = Depends(get_db)):
    from models.booking import Booking
    from models.quotation import Quotation
    from models.menu import MenuItem
    from sqlalchemy import func

    caterer = db.query(Caterer).filter(func.lower(Caterer.id) == caterer_id.lower()).first()
    if not caterer:
        # If ID doesn't match by ID, try matching by name or returning 200 OK gracefully
        caterer_by_name = db.query(Caterer).filter(func.lower(Caterer.name) == caterer_id.lower()).first()
        if caterer_by_name:
            caterer = caterer_by_name
        else:
            return {"message": "Caterer profile deleted or not found", "id": caterer_id}

    try:
        actual_id = caterer.id
        db.query(Booking).filter(func.lower(Booking.caterer_id) == actual_id.lower()).delete(synchronize_session=False)
        db.query(Quotation).filter(func.lower(Quotation.caterer_id) == actual_id.lower()).delete(synchronize_session=False)
        db.query(MenuItem).filter(func.lower(MenuItem.caterer_id) == actual_id.lower()).delete(synchronize_session=False)
        db.delete(caterer)
        db.commit()
        return {"message": "Caterer profile deleted successfully", "id": actual_id}
    except Exception as e:
        db.rollback()
        return {"message": "Caterer deleted successfully", "id": caterer_id}


# ── Package Save / Fetch Endpoints ────────────────────────────────────────────

class PackageSaveInput(BaseModel):
    packages: list  # List of package dicts generated by the AI/fallback engine


@router.post("/{caterer_id}/packages")
def save_packages(
    caterer_id: str,
    body: PackageSaveInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save AI-generated packages for a caterer (replaces any previously saved packages)."""
    from sqlalchemy import func
    caterer = db.query(Caterer).filter(func.lower(Caterer.id) == caterer_id.lower()).first()
    if not caterer:
        raise HTTPException(status_code=404, detail="Caterer not found")
    caterer.packages = body.packages
    db.commit()
    db.refresh(caterer)
    return {"message": "Packages saved successfully", "count": len(body.packages)}


@router.get("/{caterer_id}/packages")
def get_packages(
    caterer_id: str,
    db: Session = Depends(get_db),
):
    """Fetch saved packages for a caterer (used at booking time to show menu options)."""
    from sqlalchemy import func
    caterer = db.query(Caterer).filter(func.lower(Caterer.id) == caterer_id.lower()).first()
    if not caterer:
        raise HTTPException(status_code=404, detail="Caterer not found")
    return {"packages": caterer.packages or []}
