# app/api/routes/__init__.py
from fastapi import APIRouter

from . import equipment

router = APIRouter()

# include equipment endpoints
router.include_router(equipment.router)
