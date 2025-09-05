# app/api/routes/equipment.py
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_session
from app.db.models.equipment import Equipment, EquipmentStatus
from app.schemas.equipment import EquipmentCreate, EquipmentOut
from app.core.authz import require_owner, enforce_equipment_ownership
from app.db.models.user import User

router = APIRouter(prefix="/equipment", tags=["equipment"])


@router.post("/", response_model=EquipmentOut)
async def create_equipment(
    payload: EquipmentCreate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_owner),
):
    """OWNER creates a new equipment listing (draft by default)."""
    eq = Equipment(
        owner_id=user.id,
        **payload.model_dump(),
        status=EquipmentStatus.DRAFT,
    )
    session.add(eq)
    await session.commit()
    await session.refresh(eq)
    return eq


@router.get("/", response_model=List[EquipmentOut])
async def list_equipment(
    session: AsyncSession = Depends(get_session),
):
    """List all approved equipment (for borrowers)."""
    result = await session.execute(
        select(Equipment).where(Equipment.status == EquipmentStatus.APPROVED)
    )
    return result.scalars().all()


@router.get("/{equipment_id}", response_model=EquipmentOut)
async def get_equipment(
    equipment_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    eq = await session.get(Equipment, equipment_id)
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return eq


@router.patch("/{equipment_id}", response_model=EquipmentOut)
async def update_equipment(
    equipment_id: uuid.UUID,
    payload: EquipmentCreate,
    session: AsyncSession = Depends(get_session),
    eq: Equipment = Depends(enforce_equipment_ownership),
):
    """OWNER updates only their own equipment listing."""
    for field, value in payload.model_dump().items():
        setattr(eq, field, value)

    # If an approved listing is edited, push back to review
    if eq.status == EquipmentStatus.APPROVED:
        eq.status = EquipmentStatus.PENDING_REVIEW

    await session.commit()
    await session.refresh(eq)
    return eq


@router.delete("/{equipment_id}")
async def delete_equipment(
    equipment_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    eq: Equipment = Depends(enforce_equipment_ownership),
):
    """OWNER can delete only their own equipment listing."""
    if eq.status == EquipmentStatus.APPROVED:
        raise HTTPException(
            status_code=403,
            detail="Approved equipment cannot be deleted. Contact admin.",
        )

    await session.delete(eq)
    await session.commit()
    return {"message": "Equipment deleted successfully"}
