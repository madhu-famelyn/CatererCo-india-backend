from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.booking import Booking, BookingStatus
from models.quotation import Quotation, QuotationStatus
from models.caterer import Caterer
from models.user import User
from core.deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/customer")
def customer_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bookings = db.query(Booking).filter(Booking.customer_id == current_user.id).all()
    quotations = db.query(Quotation).filter(Quotation.customer_id == current_user.id).all()

    upcoming = [b for b in bookings if b.status.value in ("pending", "confirmed", "in-progress")]
    active_quotes = [q for q in quotations if q.status.value == "pending"]
    total_spent = sum(b.total for b in bookings if b.status.value == "completed")

    return {
        "stats": {
            "upcoming_events": len(upcoming),
            "active_quotations": len(active_quotes),
            "total_spent": total_spent,
            "saved_caterers": 0,
        },
        "recent_bookings": [
            {
                "id": b.id,
                "event": b.event,
                "caterer": db.query(Caterer).filter(Caterer.id == b.caterer_id).first().name if db.query(Caterer).filter(Caterer.id == b.caterer_id).first() else b.caterer_id,
                "date": b.event_date,
                "guests": b.guests,
                "total": b.total,
                "status": b.status.value,
            }
            for b in bookings[:3]
        ],
        "recent_quotations": [
            {
                "id": q.id,
                "caterer": db.query(Caterer).filter(Caterer.id == q.caterer_id).first().name if db.query(Caterer).filter(Caterer.id == q.caterer_id).first() else q.caterer_id,
                "event": q.event,
                "total": q.total,
                "status": q.status.value,
                "valid_till": q.valid_till,
            }
            for q in quotations[:3]
        ],
    }


@router.get("/caterer")
def caterer_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import func
    from datetime import datetime, timedelta

    caterer = db.query(Caterer).filter(
        (Caterer.owner_id == current_user.id) | (func.lower(Caterer.email) == current_user.email.lower())
    ).first()

    if not caterer:
        return {
            "stats": {"monthly_revenue": 0, "bookings_this_month": 0, "pending_quotations": 0, "avg_rating": 0},
            "revenue_series": [],
            "recent_bookings": [],
        }

    bookings = db.query(Booking).filter(Booking.caterer_id == caterer.id).all()
    quotations = db.query(Quotation).filter(
        Quotation.caterer_id == caterer.id,
        Quotation.status == QuotationStatus.pending,
    ).all()

    now = datetime.utcnow()
    bookings_this_month = [
        b for b in bookings 
        if b.created_at and b.created_at.month == now.month and b.created_at.year == now.year
    ]
    monthly_revenue = sum(b.total for b in bookings_this_month if b.status.value in ("confirmed", "completed"))
    bookings_count = len(bookings_this_month)

    # Build real monthly revenue series for last 6 months
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    revenue_series = []
    for i in range(5, -1, -1):
        m_date = now - timedelta(days=i * 30)
        m_label = months[m_date.month - 1]
        m_bookings = [
            b for b in bookings 
            if b.created_at and b.created_at.month == m_date.month and b.created_at.year == m_date.year
        ]
        m_rev = sum(b.total for b in m_bookings if b.status.value in ("confirmed", "completed"))
        revenue_series.append({
            "m": m_label,
            "revenue": m_rev,
            "bookings": len(m_bookings),
        })

    return {
        "stats": {
            "monthly_revenue": monthly_revenue,
            "bookings_this_month": bookings_count,
            "pending_quotations": len(quotations),
            "avg_rating": caterer.rating or 5.0,
        },
        "revenue_series": revenue_series,
        "recent_bookings": [
            {
                "id": b.id,
                "event": b.event,
                "date": b.event_date,
                "guests": b.guests,
                "total": b.total,
                "status": b.status.value,
            }
            for b in bookings[:5]
        ],
    }


@router.get("/admin")
def admin_dashboard(db: Session = Depends(get_db)):
    from datetime import datetime, timedelta

    total_bookings = db.query(Booking).count()
    bookings_list = db.query(Booking).order_by(Booking.created_at.desc()).all()
    total_revenue = sum(b.total for b in bookings_list)

    active_caterers = db.query(Caterer).filter(Caterer.is_verified == True).count()
    pending_caterers = db.query(Caterer).filter(Caterer.is_verified == False).count()
    active_customers = db.query(User).filter(User.role == "customer").count()
    pending_quotations = db.query(Quotation).filter(Quotation.status == "pending").count()

    # Dynamic 6-month aggregations for Revenue Overview and Booking Trends
    now = datetime.utcnow()
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    revenue_overview = []
    booking_trends = []

    for i in range(5, -1, -1):
        m_date = now - timedelta(days=i * 30)
        m_label = months[m_date.month - 1]
        m_bookings = [
            b for b in bookings_list
            if b.created_at and b.created_at.month == m_date.month and b.created_at.year == m_date.year
        ]
        m_rev = sum(b.total for b in m_bookings)
        revenue_overview.append({"month": m_label, "revenue": int(m_rev)})
        booking_trends.append({"month": m_label, "bookings": len(m_bookings)})

    # Format live recent bookings
    recent_bookings = []
    for b in bookings_list[:6]:
        customer = db.query(User).filter(User.id == b.customer_id).first()
        caterer = db.query(Caterer).filter(Caterer.id == b.caterer_id).first()
        recent_bookings.append({
            "id": b.id,
            "customer": f"{customer.first_name} {customer.last_name}" if customer else f"Customer #{b.customer_id}",
            "caterer": caterer.name if caterer else b.caterer_id,
            "eventType": b.event,
            "amount": int(b.total),
            "status": b.status.value if hasattr(b.status, "value") else b.status,
        })

    return {
        "stats": {
            "totalBookings": total_bookings,
            "totalRevenue": int(total_revenue),
            "activeCaterers": active_caterers,
            "activeCustomers": active_customers,
            "pendingCatererApprovals": pending_caterers,
            "pendingMenuReviews": pending_quotations,
            "openSupportTickets": 0,
        },
        "recentBookings": recent_bookings,
        "revenueOverview": revenue_overview,
        "bookingTrends": booking_trends,
    }

