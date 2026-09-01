from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from database import get_db
from models.menu import MenuItem
from models.caterer import Caterer
from models.user import User
from schemas.other import MenuItemOut, MenuItemCreate
from core.deps import get_current_user
from pydantic import BaseModel
import uuid

router = APIRouter(tags=["menu"])


class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    cuisine: Optional[str] = None
    is_vegetarian: Optional[bool] = None
    is_popular: Optional[bool] = None
    is_halal: Optional[bool] = None
    is_spicy: Optional[bool] = None


def _group_by_category(items: List[MenuItem]) -> Dict[str, List]:
    result = {}
    for item in items:
        cat = item.category
        if cat not in result:
            result[cat] = []
        result[cat].append({
            "id": item.id,
            "name": item.name,
            "price": item.price,
            "veg": item.is_vegetarian,
            "popular": item.is_popular,
            "is_halal": item.is_halal if item.is_halal is not None else True,
            "is_spicy": item.is_spicy if item.is_spicy is not None else False,
            "description": item.description,
            "cuisine": item.cuisine,
            "category": item.category,
        })
    return result


@router.get("/menu/all")
def get_all_menus(db: Session = Depends(get_db)):
    """Return menus from every caterer, grouped by caterer then category."""
    rows = db.query(MenuItem, Caterer).join(Caterer, MenuItem.caterer_id == Caterer.id).all()
    result: dict = {}
    for item, caterer in rows:
        if caterer.id not in result:
            result[caterer.id] = {
                "caterer_id": caterer.id,
                "caterer_name": caterer.name,
                "cuisine_types": caterer.cuisine_types or [],
                "tags": caterer.tags or [],
                "min_order_plates": caterer.min_order_plates if caterer.min_order_plates is not None else 0,
                "is_eco_friendly": bool(caterer.is_eco_friendly),
                "iso_14001_certified": bool(caterer.iso_14001_certified),
                "cover": caterer.cover,
                "google_rating": caterer.google_rating,
                "years_in_business": caterer.years_in_business,
                "orders_delivered": caterer.orders_delivered,
                "items": {},
            }
        cat = item.category
        if cat not in result[caterer.id]["items"]:
            result[caterer.id]["items"][cat] = []
        result[caterer.id]["items"][cat].append({
            "id": item.id,
            "name": item.name,
            "price": item.price,
            "veg": item.is_vegetarian,
            "popular": item.is_popular,
            "is_halal": item.is_halal if item.is_halal is not None else True,
            "is_spicy": item.is_spicy if item.is_spicy is not None else False,
            "description": item.description,
            "cuisine": item.cuisine,
            "category": item.category,
        })
    return list(result.values())


@router.get("/menu/{caterer_id}")
@router.get("/caterers/{caterer_id}/menu")
def get_menu(caterer_id: str, db: Session = Depends(get_db)):
    from sqlalchemy import func
    items = db.query(MenuItem).filter(func.lower(MenuItem.caterer_id) == caterer_id.lower()).all()
    return _group_by_category(items)


@router.post("/menu/{caterer_id}", status_code=201)
@router.post("/caterers/{caterer_id}/menu", status_code=201)
def add_dish(
    caterer_id: str,
    data: MenuItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    from sqlalchemy import func
    my_caterer = db.query(Caterer).filter(
        (Caterer.owner_id == current_user.id) | (func.lower(Caterer.email) == current_user.email.lower())
    ).first()
    if not my_caterer:
        raise HTTPException(status_code=403, detail="No caterer profile found for your account")
    real_caterer_id = my_caterer.id
    item_id = f"{data.category[0].lower()}{str(uuid.uuid4())[:4]}"
    item = MenuItem(
        id=item_id,
        caterer_id=real_caterer_id,
        category=data.category,
        name=data.name,
        price=data.price,
        is_vegetarian=data.is_vegetarian,
        is_popular=data.is_popular,
        is_halal=data.is_halal,
        is_spicy=data.is_spicy,
        description=data.description,
        cuisine=data.cuisine,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/caterers/{caterer_id}/menu/{item_id}")
def update_dish(
    caterer_id: str,
    item_id: str,
    data: MenuItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import func
    my_caterer = db.query(Caterer).filter(
        (Caterer.owner_id == current_user.id) | (func.lower(Caterer.email) == current_user.email.lower())
    ).first()
    if not my_caterer:
        raise HTTPException(status_code=403, detail="No caterer profile found for your account")
    item = db.query(MenuItem).filter(MenuItem.id == item_id, MenuItem.caterer_id == my_caterer.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Dish not found")
    if data.name is not None:
        item.name = data.name
    if data.category is not None:
        item.category = data.category
    if data.price is not None:
        item.price = data.price
    if data.description is not None:
        item.description = data.description
    if data.cuisine is not None:
        item.cuisine = data.cuisine
    if data.is_vegetarian is not None:
        item.is_vegetarian = data.is_vegetarian
    if data.is_popular is not None:
        item.is_popular = data.is_popular
    if data.is_halal is not None:
        item.is_halal = data.is_halal
    if data.is_spicy is not None:
        item.is_spicy = data.is_spicy
    db.commit()
    db.refresh(item)
    return {
        "id": item.id,
        "name": item.name,
        "price": item.price,
        "category": item.category,
        "veg": item.is_vegetarian,
        "popular": item.is_popular,
        "is_halal": item.is_halal if item.is_halal is not None else True,
        "is_spicy": item.is_spicy if item.is_spicy is not None else False,
        "description": item.description,
        "cuisine": item.cuisine,
    }


@router.delete("/caterers/{caterer_id}/menu/category/{category_name}", status_code=200)
def delete_category_dishes(
    caterer_id: str,
    category_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import func
    my_caterer = db.query(Caterer).filter(
        (Caterer.owner_id == current_user.id) | (func.lower(Caterer.email) == current_user.email.lower())
    ).first()
    if not my_caterer:
        raise HTTPException(status_code=403, detail="No caterer profile found for your account")
    
    deleted_count = db.query(MenuItem).filter(
        MenuItem.caterer_id == my_caterer.id,
        func.lower(MenuItem.category) == category_name.lower()
    ).delete(synchronize_session=False)
    db.commit()
    return {"message": f"Deleted {deleted_count} dishes from {category_name}", "deleted_count": deleted_count}


@router.delete("/caterers/{caterer_id}/menu/{item_id}", status_code=204)
def delete_dish(
    caterer_id: str,
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import func
    my_caterer = db.query(Caterer).filter(
        (Caterer.owner_id == current_user.id) | (func.lower(Caterer.email) == current_user.email.lower())
    ).first()
    if not my_caterer:
        raise HTTPException(status_code=403, detail="No caterer profile found for your account")
    item = db.query(MenuItem).filter(MenuItem.id == item_id, MenuItem.caterer_id == my_caterer.id).first()
    if item:
        db.delete(item)
        db.commit()



