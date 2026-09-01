from routers.auth import router as auth_router
from routers.caterers import router as caterers_router
from routers.bookings import router as bookings_router
from routers.quotations import router as quotations_router
from routers.menu import router as menu_router
from routers.events import router as events_router
from routers.notifications import router as notifications_router
from routers.dashboard import router as dashboard_router
from routers.users import router as users_router
from routers.gallery import router as gallery_router
from routers.upload import router as upload_router
from routers.support import router as support_router
from routers.reviews import router as reviews_router

__all__ = [
    "auth_router", "caterers_router", "bookings_router", "quotations_router",
    "menu_router", "events_router", "notifications_router", "dashboard_router",
    "users_router", "gallery_router", "upload_router", "support_router", "reviews_router",
]
