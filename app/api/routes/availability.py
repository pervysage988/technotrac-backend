from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID

from app.db.session import get_session
from app.db.models.availability import Availability
from app.db.models.equipment import Equipment
from app.schemas.availability import AvailabilityCreate, AvailabilityOut
from app.utils.jwt import require_role

router = APIRouter(prefix="/availability", tags=["availability"])


@router.post("/", response_model=AvailabilityOut)
async def create_availability(
    payload: AvailabilityCreate,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_role("OWNER"))
):
    # Ensure equipment exists
    res = await session.execute(select(Equipment).where(Equipment.id == payload.equipment_id))
    equipment = res.scalar_one_or_none()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    # Check overlap for same equipment
    overlap_query = await session.execute(
        select(Availability).where(
            and_(
                Availability.equipment_id == payload.equipment_id,
                Availability.start_time < payload.end_time,
                Availability.end_time > payload.start_time,
            )
        )
    )
    if overlap_query.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Overlapping availability exists")

    availability = Availability(
        equipment_id=payload.equipment_id,
        owner_id=user.id,
        start_time=payload.start_time,
        end_time=payload.end_time,
    )
    session.add(availability)
    await session.commit()
    await session.refresh(availability)
    return availability


@router.get("/{equipment_id}", response_model=list[AvailabilityOut])
async def list_availability(
    equipment_id: UUID,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_role("OWNER", "FARMER"))
):
    res = await session.execute(
        select(Availability).where(Availability.equipment_id == equipment_id)
    )
    return list(res.scalars())
