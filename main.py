# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from alembic import command
from alembic.config import Config
import os

# Import your routers
from app.api.routes import equipment, bookings, auth, availability, admin, payments, ratings

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with proper prefixes
app.include_router(auth.router, prefix="/api/auth")
app.include_router(equipment.router, prefix="/api/equipment")
app.include_router(bookings.router, prefix="/api/bookings")
app.include_router(availability.router, prefix="/api/availability")
app.include_router(admin.router, prefix="/api/admin")
app.include_router(payments.router, prefix="/api/payments")
app.include_router(ratings.router, prefix="/api/ratings")

@app.on_event("startup")
def run_migrations():
    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("✅ Alembic migrations applied")
    except Exception as e:
        print(f"⚠️ Migration failed: {e}")

@app.get("/")
def read_root():
    return {"message": "Welcome to Technotrac"}
