# app/auth.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.models.user import User, UserRole
from app.services.otp import send_otp, verify_otp
from app.utils.jwt import create_jwt_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


# ------------------------
# Schemas
# ------------------------
class OTPRequest(BaseModel):
    phone: str


class OTPVerify(BaseModel):
    phone: str
    code: str
    role: UserRole  # FARMER or OWNER


# ------------------------
# Routes
# ------------------------
@router.post("/otp/request")
async def otp_request(data: OTPRequest):
    await send_otp(data.phone)
    return {"message": f"OTP sent to {data.phone}"}


@router.post("/otp/verify")
async def otp_verify(data: OTPVerify):
    is_valid = await verify_otp(data.phone, data.code)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.phone_e164 == data.phone)
        )
        user = result.scalar_one_or_none()
        if not user:
            user = User(phone_e164=data.phone, role=data.role)
            session.add(user)
            await session.commit()
            await session.refresh(user)

    token = create_jwt_token({
        "sub": str(user.id),
        "role": user.role.value
    })
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
async def read_current_user(current_user: User = Depends(get_current_user)):
    """Return the currently logged in user (from JWT)."""
    return {
        "id": str(current_user.id),
        "phone": current_user.phone_e164,
        "role": current_user.role.value,
    }
