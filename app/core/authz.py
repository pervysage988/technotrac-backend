from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_user, require_owner
from app.db.models.user import User, UserRole
from app.db.models.equipment import Equipment
from app.db.models.booking import Booking
from app.db.session import get_session
from uuid import UUID


# -------- Ownership / Access checks --------
async def enforce_equipment_ownership(
    equipment_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_owner),
) -> Equipment:
    """Ensure the equipment belongs to the current OWNER user."""
    eq = await session.get(Equipment, equipment_id)
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")

    if eq.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not your equipment")

    return eq


async def enforce_booking_access(
    booking_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Booking:
    """
    Allow FARMER (renter) or OWNER (equipment owner) to access booking.
    Admins can also access.
    """
    booking = await session.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if user.role == UserRole.ADMIN:
        return booking

    if user.role == UserRole.FARMER and booking.renter_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if user.role == UserRole.OWNER:
        eq = await session.get(Equipment, booking.equipment_id)
        if not eq or eq.owner_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized")

    return booking
