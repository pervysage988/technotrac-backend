 
# app/api/routes/payment.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.db.session import get_session
from app.db.models.payment import Payment, PaymentStatus
from app.db.models.booking import Booking, BookingStatus
from app.schemas.payment import PaymentIntentCreate, PaymentIntentOut
from app.utils.jwt import require_role

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/intent", response_model=PaymentIntentOut)
async def create_payment_intent(
    payload: PaymentIntentCreate,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_role("FARMER", "OWNER"))
):
    # Booking must exist
    booking = await session.get(Booking, payload.booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    payment = Payment(
        booking_id=payload.booking_id,
        method=payload.method,
    )
    session.add(payment)
    await session.commit()
    await session.refresh(payment)
    return payment


@router.post("/{payment_id}/confirm", response_model=PaymentIntentOut)
async def confirm_payment(
    payment_id: UUID,
    session: AsyncSession = Depends(get_session),
    user=Depends(require_role("FARMER", "OWNER"))
):
    payment = await session.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # For now, always succeed
    payment.status = PaymentStatus.PAID

    # Also mark booking as COMPLETED
    booking = await session.get(Booking, payment.booking_id)
    if booking:
        booking.status = BookingStatus.COMPLETED

    await session.commit()
    await session.refresh(payment)
    return payment
