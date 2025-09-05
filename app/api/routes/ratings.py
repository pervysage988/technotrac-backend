# app/api/routes/ratings.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.db.session import get_session
from app.db.models.rating import Rating
from app.db.models.booking import Booking, BookingStatus
from app.db.models.equipment import Equipment  # ✅ needed for owner_id
from app.schemas.rating import RatingCreate, RatingOut
from app.core.security import require_role  # fixed import (utils.jwt → core.security)

router = APIRouter(prefix="/ratings", tags=["ratings"])


# ------------------------
# Create a new rating
# ------------------------
@router.post("/", response_model=RatingOut)
async def create_rating(
    payload: RatingCreate,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_role("FARMER", "OWNER")),
):
    # Make sure booking exists
    booking = await session.get(Booking, payload.booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Ensure booking is completed before rating
    if booking.status != BookingStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Can only rate after booking is completed")

    # Prevent duplicate rating
    q = select(Rating).where(Rating.booking_id == booking.id)
    res = await session.execute(q)
    if res.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Rating already submitted for this booking")

    # Load equipment (to get owner_id)
    equipment = await session.get(Equipment, booking.equipment_id)

    # Who is rating who?
    if user["sub"] == str(booking.renter_id):  # farmer rating owner
        by_user_id = booking.renter_id
        for_user_id = equipment.owner_id
    elif user["sub"] == str(equipment.owner_id):  # owner rating farmer
        by_user_id = equipment.owner_id
        for_user_id = booking.renter_id
    else:
        raise HTTPException(status_code=403, detail="Not allowed to rate this booking")

    rating = Rating(
        booking_id=booking.id,
        by_user_id=by_user_id,
        for_user_id=for_user_id,
        stars=payload.stars,
        comment=payload.comment,
    )
    session.add(rating)
    await session.commit()
    await session.refresh(rating)
    return rating


# ------------------------
# Get ratings for a user
# ------------------------
@router.get("/user/{user_id}", response_model=list[RatingOut])
async def get_user_ratings(
    user_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    q = select(Rating).where(Rating.for_user_id == user_id)
    res = await session.execute(q)
    return list(res.scalars())
