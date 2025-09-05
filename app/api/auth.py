# app/api/auth.py
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel

from app.db.session import get_session
from app.utils.phone import validate_phone_e164
from app.db.models.user import User, UserRole, FarmerProfile, OwnerProfile, KycStatus
from app.schemas.user import UserRead, FarmerProfileRead, OwnerProfileRead
from app.services.otp import send_otp, verify_otp
from app.core.security import create_access_token
from app.core.rate_limit import check_rate_limit
from app.core.logging import mask_phone, logger

router = APIRouter(prefix="/auth", tags=["auth"])


# ------------------------
# Request Schemas
# ------------------------
class PhoneRequest(BaseModel):
    phone_e164: str


class VerifyOtpRequest(BaseModel):
    phone_e164: str
    code: str
    role: UserRole


class SwitchRoleRequest(BaseModel):
    role: UserRole


class FarmerProfileUpdate(BaseModel):
    village: str | None = None
    pincode: str | None = None


class OwnerProfileUpdate(BaseModel):
    upi_id: str | None = None
    kyc_status: KycStatus | None = None


# ------------------------
# Auth Routes
# ------------------------
@router.post("/otp/request")
async def send_otp_route(
    payload: PhoneRequest,
    request: Request,
    db: AsyncSession = Depends(get_session),
):
    """
    Step 1: User enters phone number.
    -> Validate + rate limit
    -> Send OTP via provider (Twilio/MSG91/etc.)
    """
    phone = validate_phone_e164(payload.phone_e164)

    # Rate limit (phone + IP based)
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(f"otp:{phone}", limit=5, window=60)      # 5 per minute per phone
    check_rate_limit(f"otp-ip:{client_ip}", limit=20, window=60)  # 20 per minute per IP

    await send_otp(phone, db)

    logger.info(f"OTP requested for {mask_phone(phone)} from IP={client_ip}")
    return {"message": "OTP sent successfully"}


@router.post("/otp/verify")
async def verify_otp_route(
    payload: VerifyOtpRequest,
    db: AsyncSession = Depends(get_session)
):
    """
    Step 2: User enters received OTP.
    -> Verify OTP
    -> If new user, create entry + default profile
    -> Return JWT token
    """
    phone = validate_phone_e164(payload.phone_e164)

    if not await verify_otp(phone, payload.code):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # Check if user exists
    result = await db.execute(select(User).where(User.phone_e164 == phone))
    user = result.scalars().first()

    if not user:
        # First-time login -> create user & profile
        user = User(phone_e164=phone, role=payload.role)
        db.add(user)
        await db.flush()

        if payload.role == UserRole.FARMER:
            db.add(FarmerProfile(user_id=user.id))
        elif payload.role == UserRole.OWNER:
            db.add(OwnerProfile(user_id=user.id))

        await db.commit()
        await db.refresh(user)

    # Issue JWT
    token = create_access_token({"sub": str(user.id), "role": user.role.value})

    logger.info(f"OTP verified for {mask_phone(phone)} -> user_id={user.id}")
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": str(user.id), "role": user.role.value},
    }
