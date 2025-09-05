# app/api/routes/booking.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from math import ceil

from app.db.session import get_session
from app.db.models.booking import Booking, BookingStatus
from app.db.models.equipment import Equipment
from app.schemas.booking import BookingCreate, BookingOut
from app.core.security import get_current_user
from app.core.authz import (
    require_farmer,
    require_owner,
    enforce_booking_access,
)

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("/", response_model=BookingOut)
async def create_booking(
    payload: BookingCreate,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_farmer),
):
    # Ensure equipment exists
    res = await session.execute(
        select(Equipment).where(Equipment.id == payload.equipment_id)
    )
    equipment = res.scalar_one_or_none()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    # Pricing logic
    duration = payload.end_ts - payload.start_ts
    if duration.total_seconds() <= 0:
        raise HTTPException(status_code=400, detail="Invalid booking duration")

    days = duration.days
    hours = duration.seconds // 3600

    if days >= 1:
        price_total = equipment.daily_rate * ceil(days)
    elif equipment.hourly_rate:
        price_total = equipment.hourly_rate * max(hours, 1)
    else:
        price_total = equipment.daily_rate

    commission_fee = round(price_total * 0.10)
    owner_payout = price_total - commission_fee

    booking = Booking(
        equipment_id=payload.equipment_id,
        renter_id=user.id,
        start_ts=payload.start_ts,
        end_ts=payload.end_ts,
        status=BookingStatus.PENDING,
        price_total=price_total,
        commission_fee=commission_fee,
        owner_payout=owner_payout,
    )
    session.add(booking)
    await session.commit()
    await session.refresh(booking)
    return booking


@router.get("/{booking_id}", response_model=BookingOut)
async def get_booking(
    booking: Booking = Depends(enforce_booking_access),
):
    return booking


@router.patch("/{booking_id}/accept", response_model=BookingOut)
async def accept_booking(
    booking_id: UUID,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_owner),
):
    booking = await session.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    eq = await session.get(Equipment, booking.equipment_id)
    if not eq or eq.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    booking.status = BookingStatus.ACCEPTED
    await session.commit()
    await session.refresh(booking)
    return booking


@router.patch("/{booking_id}/reject", response_model=BookingOut)
async def reject_booking(
    booking_id: UUID,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_owner),
):
    booking = await session.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    eq = await session.get(Equipment, booking.equipment_id)
    if not eq or eq.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    booking.status = BookingStatus.REJECTED
    await session.commit()
    await session.refresh(booking)
    return booking


@router.patch("/{booking_id}/cancel", response_model=BookingOut)
async def cancel_booking(
    booking: Booking = Depends(enforce_booking_access),
    session: AsyncSession = Depends(get_session),
):
    booking.status = BookingStatus.CANCELLED
    await session.commit()
    await session.refresh(booking)
    return booking


@router.patch("/{booking_id}/complete", response_model=BookingOut)
async def complete_booking(
    booking_id: UUID,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_owner),
):
    booking = await session.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    eq = await session.get(Equipment, booking.equipment_id)
    if not eq or eq.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if booking.status != BookingStatus.ACCEPTED:
        raise HTTPException(status_code=400, detail="Booking must be ACCEPTED before completing")

    booking.status = BookingStatus.COMPLETED
    await session.commit()
    await session.refresh(booking)
    return booking


@router.get("/my", response_model=list[BookingOut])
async def list_my_bookings(
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    q = select(Booking)
    if user.role == "FARMER":
        q = q.where(Booking.renter_id == user.id)
    else:
        q = q.join(Equipment).where(Equipment.owner_id == user.id)

    res = await session.execute(q)
    return list(res.scalars())
