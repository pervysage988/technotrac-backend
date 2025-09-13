from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import logger

# Routers
from app.api import auth
from app.api.routes import media
from app.api.routes.equipment import router as equipment_router
from app.api.routes.booking import router as booking_router
from app.api.routes.availability import router as availability_router
from app.api.routes.admin import router as admin_router
from app.api.routes.payment import router as payment_router
from app.api.routes.ratings import router as ratings_router

from app.db import base  # ensures all models are registered

import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from alembic import command
from alembic.config import Config
from pathlib import Path

# --------------------------------------------------
# Create FastAPI app
# --------------------------------------------------
app = FastAPI(title=settings.app_name, debug=settings.debug)

# --------------------------------------------------
# ✅ Debug: Check if REDIS_URL is loaded from env
# --------------------------------------------------
redis_url = os.getenv("REDIS_URL")
if redis_url:
    logger.info(f"✅ REDIS_URL loaded: {redis_url[:30]}... (masked)")
else:
    logger.warning("⚠️ REDIS_URL not found in environment!")

# --------------------------------------------------
# ✅ CORS setup for local, Firebase, and Vercel
# --------------------------------------------------
cors_origins = [
    "https://technotrac.web.app",             # Firebase Hosting
    "https://technotrac.firebaseapp.com",     # Firebase alternate domain
    "http://localhost:3000",                  # local frontend dev
    "http://localhost:5173",                  # Vite dev server
    "https://technotrac-frontend.vercel.app", # Vercel production frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# ✅ Auto-run Alembic migrations on startup
# --------------------------------------------------
@app.on_event("startup")
async def run_migrations():
    def _upgrade():
        try:
            BASE_DIR = Path(__file__).resolve().parent.parent
            alembic_cfg = Config(str(BASE_DIR / "alembic.ini"))
            # Force DB URL for Render
            alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)
            command.upgrade(alembic_cfg, "head")
            logger.info("✅ Alembic migrations applied successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to run migrations: {e}")

    loop = asyncio.get_event_loop()
    # Run migrations in background thread so startup isn’t blocked
    await loop.run_in_executor(ThreadPoolExecutor(), _upgrade)

# --------------------------------------------------
# ✅ Register routers
# --------------------------------------------------
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(equipment_router, prefix="/api/equipment", tags=["equipment"])
app.include_router(booking_router, prefix="/api/bookings", tags=["bookings"])
app.include_router(availability_router, prefix="/api/availability", tags=["availability"])
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
app.include_router(payment_router, prefix="/api/payments", tags=["payments"])
app.include_router(ratings_router, prefix="/api/ratings", tags=["ratings"])
app.include_router(media.router, prefix="/api/media", tags=["media"])

# ----------------------------
# Test route to check backend connection
# ----------------------------
@app.get("/api/test")
def test_api():
    return {"message": "CORS is working!"}

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
