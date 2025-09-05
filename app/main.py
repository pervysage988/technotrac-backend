from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import logger

# Routers
from app.api import auth
from app.api.routes import media
from app.api.routes import router as api_router
from app.api.routes.equipment import router as equipment_router
from app.api.routes.booking import router as booking_router
from app.api.routes.availability import router as availability_router
from app.api.routes.admin import router as admin_router
from app.api.routes.payment import router as payment_router
from app.api.routes.ratings import router as ratings_router
from app.api import auth as auth_router

from app.db.base_class import Base
from app.db import base  # ensures all models are registered
from app.db.session import engine


# --------------------------------------------------
# Create FastAPI app
# --------------------------------------------------
app = FastAPI(title=settings.app_name, debug=settings.debug)

# ✅ CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Register routers
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(equipment_router, prefix="/api/equipment", tags=["equipment"])
app.include_router(booking_router, prefix="/api/bookings", tags=["bookings"])
app.include_router(availability_router, prefix="/api/availability", tags=["availability"])
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
app.include_router(payment_router, prefix="/api/payments", tags=["payments"])
app.include_router(ratings_router, prefix="/api/ratings", tags=["ratings"])
app.include_router(media.router, prefix="/api/media", tags=["media"])


# --------------------------------------------------
# Root endpoint
# --------------------------------------------------
@app.get("/")
def root():
    return {"message": "Welcome to TechnoTrac API"}


# --------------------------------------------------
# Global exception handler
# --------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error occurred")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )
