# app/core/authz.py
from fastapi import Depends, HTTPException, status
from app.core.security import get_current_user
from app.db.models.user import UserRole, User
from app.db.models.equipment import Equipment
from app.db.models.booking import Booking
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from uuid import UUID


# -------- Role checks --------
def require_owner(user: User = Depends(get_current_user)) -> User:
    """Allow only OWNER role users."""
    if user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only equipment owners can perform this action",
        )
    return user


def require_farmer(user: User = Depends(get_current_user)) -> User:
    """Allow only FARMER role users."""
    if user.role != UserRole.FARMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only farmers can perform this action",
        )
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """Allow only ADMIN role users."""
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can perform this action",
        )
    return user


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
    """Allow FARMER (renter) or OWNER (equipment owner) to access booking."""
    booking = await session.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if user.role == UserRole.FARMER and booking.renter_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if user.role == UserRole.OWNER:
        eq = await session.get(Equipment, booking.equipment_id)
        if not eq or eq.owner_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized")

    return booking
