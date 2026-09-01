import os
import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import ResponseValidationError
from database import engine, Base
from routers import (
    auth_router, caterers_router, bookings_router, quotations_router,
    menu_router, events_router, notifications_router, dashboard_router,
    users_router, gallery_router, upload_router, support_router, reviews_router,
)

app = FastAPI(
    title="CatererCo UAE API",
    description="Backend for the UAE Catering Marketplace",
    version="1.0.0",
)

# Ensure local fallback upload directory exists and is mounted
os.makedirs("static_uploads", exist_ok=True)
app.mount("/static_uploads", StaticFiles(directory="static_uploads"), name="static_uploads")

# ── CORS ─────────────────────────────────────────────────────────────────────
# allow_credentials=True requires explicit origins — wildcard "*" is not allowed.
# allow_origin_regex covers every http://localhost:<any-port> for dev,
# plus all HTTPS origins for production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:4173",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:8080",
        "http://localhost:8081",
        "http://localhost:8082",
        "http://localhost:8083",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8081",
    ],
    allow_origin_regex=r"http://localhost(:\d+)?|http://127\.0\.0\.1(:\d+)?|https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global exception handlers ─────────────────────────────────────────────────
# These are registered INSIDE the app (inside the CORS middleware layer).
# This means any 500 response they return will automatically get CORS headers added
# by the CORSMiddleware above — preventing the misleading "CORS blocked" error
# that the browser shows when an unhandled exception bypasses the CORS headers.

@app.exception_handler(ResponseValidationError)
async def response_validation_error_handler(request: Request, exc: ResponseValidationError):
    """Schema mismatch between DB data and Pydantic response model (e.g. NULL field vs List[str])."""
    print(f"[ResponseValidationError] {request.method} {request.url}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": "Response serialisation error — check server logs for details"},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all for any other unhandled server-side exception."""
    print(f"[UnhandledException] {type(exc).__name__}: {exc}  →  {request.method} {request.url}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error ({type(exc).__name__})"},
    )
# ─────────────────────────────────────────────────────────────────────────────

# Direct routers
app.include_router(auth_router)
app.include_router(caterers_router)
app.include_router(bookings_router)
app.include_router(quotations_router)
app.include_router(menu_router)
app.include_router(events_router)
app.include_router(notifications_router)
app.include_router(dashboard_router)
app.include_router(users_router)
app.include_router(gallery_router)
app.include_router(upload_router)
app.include_router(support_router)
app.include_router(reviews_router)

# /api/v1 versioned routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(caterers_router, prefix="/api/v1")
app.include_router(bookings_router, prefix="/api/v1")
app.include_router(quotations_router, prefix="/api/v1")
app.include_router(menu_router, prefix="/api/v1")
app.include_router(events_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(reviews_router, prefix="/api/v1")

# /v1 stripped routers (for frontends that proxy-strip /api)
app.include_router(auth_router, prefix="/v1")
app.include_router(caterers_router, prefix="/v1")
app.include_router(bookings_router, prefix="/v1")
app.include_router(quotations_router, prefix="/v1")
app.include_router(menu_router, prefix="/v1")
app.include_router(events_router, prefix="/v1")
app.include_router(notifications_router, prefix="/v1")
app.include_router(dashboard_router, prefix="/v1")
app.include_router(users_router, prefix="/v1")
app.include_router(reviews_router, prefix="/v1")


@app.get("/")
def root():
    return {"status": "ok", "message": "CatererCo Global API is running 🚀"}


@app.get("/health")
def health():
    return {"status": "healthy"}
