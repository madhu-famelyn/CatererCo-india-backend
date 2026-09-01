"""
Seed the database with mock data for Indian catering (Bangalore & Hyderabad).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import engine, SessionLocal, Base
from models.user import User, UserRole
from models.caterer import Caterer
from models.menu import MenuItem
from models.booking import Booking, BookingStatus
from models.quotation import Quotation, QuotationStatus
from models.notification import Notification
from core.security import hash_password

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()


def seed():
    # ── Clear existing data ─────────────────────────────────────────────────
    db.query(Notification).delete()
    db.query(Quotation).delete()
    db.query(Booking).delete()
    db.query(MenuItem).delete()
    db.query(Caterer).delete()
    db.query(User).delete()
    db.commit()

    # ── Users ───────────────────────────────────────────────────────────────
    customer = User(
        first_name="Sonu",
        last_name="Sah",
        email="sonusah22388@gmail.com",
        phone="+919876543210",
        hashed_password=hash_password("password123"),
        role=UserRole.customer,
        is_verified=True,
        preferred_emirate="Bangalore",
        language="English",
    )
    caterer_user = User(
        first_name="Rajesh",
        last_name="Sharma",
        email="caterer@royalrasoi.in",
        phone="+919888877777",
        hashed_password=hash_password("password123"),
        role=UserRole.caterer,
        is_verified=True,
    )
    db.add_all([customer, caterer_user])
    db.commit()

    # ── Caterers ─────────────────────────────────────────────────────────────
    caterers_data = [
        {
            "id": "c1", "name": "Royal Rasoi Banquet & Catering", "rating": 4.9, "reviews": 312,
            "location": "Indiranagar, Bangalore", "tags": ["North Indian", "Mughlai", "Weddings"],
            "starting_from": 450, "owner_id": caterer_user.id,
            "cover": "https://images.unsplash.com/photo-1555244162-803834f70033?w=800",
            "about": "Premier luxury royal Indian catering with royal thalis, kebabs, and live tandoor stations.",
            "emirate": "Bangalore", "certifications": ["FSSAI Certified", "ISO 22000"],
            "trade_license": "FSSAI-1122334455", "vat_number": "GSTIN29ABCDE1234F1Z5",
            "contact_person": "Rajesh Sharma", "email": "caterer@royalrasoi.in",
            "phone": "+919888877777", "address": "100ft Road, Indiranagar, Bangalore",
            "chefs": 14, "waiters": 40, "multilingual_staff": 10,
        },
        {
            "id": "c2", "name": "Zafran Live Kitchen", "rating": 4.8, "reviews": 198,
            "location": "Hitec City, Hyderabad", "tags": ["Live Stations", "Tandoor", "Corporate"],
            "starting_from": 550, "owner_id": None,
            "cover": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800",
            "about": "Interactive live cooking stations and signature Biryani cauldrons for corporate and wedding galas.",
            "emirate": "Hyderabad", "certifications": ["FSSAI Certified", "HACCP"],
        },
        {
            "id": "c3", "name": "Dakshin Heritage Catering", "rating": 4.7, "reviews": 145,
            "location": "Koramangala, Bangalore", "tags": ["South Indian", "Pure Veg & Jain", "Karnataka Special"],
            "starting_from": 350, "owner_id": None,
            "cover": "https://images.unsplash.com/photo-1544025162-d76694265947?w=800",
            "about": "Authentic traditional South Indian plantain leaf feasts, filter coffee, and Satvik Jain preparations.",
            "emirate": "Bangalore", "certifications": ["FSSAI Certified", "100% Pure Veg"],
        },
        {
            "id": "c4", "name": "The Grand Nizam", "rating": 4.9, "reviews": 284,
            "location": "Jubilee Hills, Hyderabad", "tags": ["Hyderabadi & Biryani", "Mughlai", "Luxury"],
            "starting_from": 600, "owner_id": None,
            "cover": "https://images.unsplash.com/photo-1519671482749-fd09be7ccebf?w=800",
            "about": "World-famous Hyderabadi Dum Biryani, Haleem, and royal Nawabi banqueting for grand events.",
            "emirate": "Hyderabad", "certifications": ["FSSAI Certified", "ISO 9001"],
        },
        {
            "id": "c5", "name": "Saffron Sweets & Banquet", "rating": 4.8, "reviews": 176,
            "location": "Whitefield, Bangalore", "tags": ["Weddings", "Pure Veg", "Desserts & Mithai"],
            "starting_from": 400, "owner_id": None,
            "cover": "https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=800",
            "about": "Gourmet vegetarian catering featuring live chaat counters, artisanal Indian sweets, and regional delights.",
            "emirate": "Bangalore", "certifications": ["FSSAI Certified"],
        },
        {
            "id": "c6", "name": "Telangana Spice Co.", "rating": 4.8, "reviews": 160,
            "location": "Banjara Hills, Hyderabad", "tags": ["Andhra & Telangana", "Tandoor", "House Party"],
            "starting_from": 480, "owner_id": None,
            "cover": "https://images.unsplash.com/photo-1555244162-803834f70033?w=800",
            "about": "Spicy and aromatic authentic Andhra & Telangana culinary specialties and live BBQ grills.",
            "emirate": "Hyderabad", "certifications": ["FSSAI Certified"],
        },
    ]

    for c_data in caterers_data:
        c = Caterer(
            id=c_data["id"],
            name=c_data["name"],
            rating=c_data["rating"],
            reviews=c_data["reviews"],
            location=c_data["location"],
            tags=c_data["tags"],
            starting_from=c_data["starting_from"],
            cover=c_data.get("cover"),
            about=c_data.get("about"),
            emirate=c_data.get("emirate"),
            certifications=c_data.get("certifications", []),
            owner_id=c_data.get("owner_id"),
            trade_license=c_data.get("trade_license"),
            vat_number=c_data.get("vat_number"),
            contact_person=c_data.get("contact_person"),
            email=c_data.get("email"),
            phone=c_data.get("phone"),
            address=c_data.get("address"),
            chefs=c_data.get("chefs", 0),
            waiters=c_data.get("waiters", 0),
            multilingual_staff=c_data.get("multilingual_staff", 0),
            is_verified=True,
        )
        db.add(c)
    db.commit()

    # ── Menu items for c1 ────────────────────────────────────────────────────
    menu_data = [
        {"id": "s1", "caterer_id": "c1", "category": "starters", "name": "Paneer Tikka with Mint Chutney", "price": 120, "is_vegetarian": True},
        {"id": "s2", "caterer_id": "c1", "category": "starters", "name": "Murgh Malai Kebab", "price": 180, "is_vegetarian": False},
        {"id": "s3", "caterer_id": "c1", "category": "starters", "name": "Crispy Corn Pepper Salt", "price": 90, "is_vegetarian": True},
        {"id": "s4", "caterer_id": "c1", "category": "starters", "name": "Dahi Ke Kebab", "price": 110, "is_vegetarian": True},
        {"id": "m1", "caterer_id": "c1", "category": "mains", "name": "Hyderabadi Dum Biryani with Mirchi Salan", "price": 250, "is_vegetarian": False, "is_popular": True},
        {"id": "m2", "caterer_id": "c1", "category": "mains", "name": "Paneer Butter Masala", "price": 180, "is_vegetarian": True},
        {"id": "m3", "caterer_id": "c1", "category": "mains", "name": "Dal Makhani with Garlic Naan", "price": 150, "is_vegetarian": True},
        {"id": "m4", "caterer_id": "c1", "category": "mains", "name": "Butter Chicken with Tandoori Roti", "price": 220, "is_vegetarian": False},
        {"id": "d1", "caterer_id": "c1", "category": "desserts", "name": "Gulab Jamun with Rabri", "price": 80, "is_vegetarian": True, "is_popular": True},
        {"id": "d2", "caterer_id": "c1", "category": "desserts", "name": "Rasmalai Platter", "price": 100, "is_vegetarian": True},
        {"id": "d3", "caterer_id": "c1", "category": "desserts", "name": "Kulfi Falooda", "price": 90, "is_vegetarian": True},
        {"id": "b1", "caterer_id": "c1", "category": "beverages", "name": "Masala Chai & Filter Coffee Station", "price": 40, "is_vegetarian": True},
        {"id": "b2", "caterer_id": "c1", "category": "beverages", "name": "Fresh Mango Lassi", "price": 60, "is_vegetarian": True},
        {"id": "b3", "caterer_id": "c1", "category": "beverages", "name": "Mint Masala Chaas", "price": 45, "is_vegetarian": True},
    ]
    for m in menu_data:
        db.add(MenuItem(
            id=m["id"], caterer_id=m["caterer_id"], category=m["category"],
            name=m["name"], price=m["price"],
            is_vegetarian=m.get("is_vegetarian", False),
            is_popular=m.get("is_popular", False),
        ))
    db.commit()

    # ── Bookings ─────────────────────────────────────────────────────────────
    bookings_data = [
        {"id": "BK-1042", "caterer_id": "c1", "event": "Wedding Reception", "event_date": "2026-08-14", "guests": 250, "total": 65000, "status": BookingStatus.confirmed},
        {"id": "BK-1041", "caterer_id": "c2", "event": "Corporate Gala", "event_date": "2026-07-22", "guests": 100, "total": 55000, "status": BookingStatus.in_progress},
        {"id": "BK-1040", "caterer_id": "c3", "event": "House Warming Puja", "event_date": "2026-07-18", "guests": 50, "total": 22500, "status": BookingStatus.pending},
        {"id": "BK-1039", "caterer_id": "c4", "event": "Sangeet Night", "event_date": "2026-06-30", "guests": 120, "total": 56000, "status": BookingStatus.completed},
    ]
    for b in bookings_data:
        db.add(Booking(
            id=b["id"], customer_id=customer.id,
            caterer_id=b["caterer_id"], event=b["event"],
            event_date=b["event_date"], guests=b["guests"],
            total=b["total"], status=b["status"],
        ))
    db.commit()

    # ── Quotations ───────────────────────────────────────────────────────────
    quotations_data = [
        {"id": "QT-2201", "caterer_id": "c1", "event": "Wedding Reception", "guests": 250, "total": 65000, "valid_till": "2026-07-30", "status": QuotationStatus.pending},
        {"id": "QT-2200", "caterer_id": "c4", "event": "Sangeet Night", "guests": 120, "total": 56000, "valid_till": "2026-07-28", "status": QuotationStatus.pending},
        {"id": "QT-2199", "caterer_id": "c2", "event": "Corporate Gala", "guests": 100, "total": 55000, "valid_till": "2026-07-15", "status": QuotationStatus.approved},
    ]
    for q in quotations_data:
        db.add(Quotation(
            id=q["id"], customer_id=customer.id,
            caterer_id=q["caterer_id"], event=q["event"],
            guests=q["guests"], total=q["total"],
            valid_till=q["valid_till"], status=q["status"],
        ))
    db.commit()

    # ── Notifications ─────────────────────────────────────────────────────────
    notifs = [
        {"title": "Quotation received", "body": "Royal Rasoi Banquet sent a quotation for your wedding.", "time_label": "2h ago", "unread": True},
        {"title": "Menu updated", "body": "AI suggested 3 replacements to fit your budget.", "time_label": "5h ago", "unread": True},
        {"title": "Booking confirmed", "body": "BK-1039 marked completed. Please leave a review.", "time_label": "1d ago", "unread": False},
    ]
    for n in notifs:
        db.add(Notification(user_id=customer.id, **n))
    db.commit()

    print("✅ Database created and seeded successfully on Neon PostgreSQL!")
    print(f"   👤 Customer: {customer.email} / password123")
    print(f"   🍽️  Caterer:  {caterer_user.email} / password123")
    print(f"   📦 {len(caterers_data)} caterers, {len(menu_data)} menu items")
    print(f"   📋 {len(bookings_data)} bookings, {len(quotations_data)} quotations")


if __name__ == "__main__":
    seed()
    db.close()
