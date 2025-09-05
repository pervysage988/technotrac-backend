from pydantic import BaseModel, validator, Field
from datetime import datetime
from enum import Enum
from uuid import UUID


class BookingStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"


class BookingCreate(BaseModel):
    equipment_id: UUID
    start_ts: datetime
    end_ts: datetime

    @validator("end_ts")
    def end_after_start(cls, v, values):
        """Ensure booking end is strictly after start."""
        if "start_ts" in values and v <= values["start_ts"]:
            raise ValueError("end_ts must be after start_ts")
        return v

    @validator("start_ts")
    def start_in_future(cls, v):
        """Ensure booking cannot start in the past."""
        if v < datetime.utcnow():
            raise ValueError("start_ts must be in the future")
        return v


class BookingUpdate(BaseModel):
    """Used by Farmer/Owner to update booking status (PATCH)."""
    status: BookingStatus


class BookingOut(BaseModel):
    id: UUID
    equipment_id: UUID
    farmer_id: UUID   # exposed field; internally == renter_id in DB
    status: BookingStatus
    start_ts: datetime
    end_ts: datetime
    created_at: datetime

    # 💰 Pricing fields
    price_total: int = Field(..., ge=0)
    commission_fee: int = Field(..., ge=0)
    owner_payout: int = Field(..., ge=0)

    class Config:
        from_attributes = True
        fields = {
            "farmer_id": "renter_id"  # DB field → API alias
        }
        json_schema_extra = {
            "notes": "farmer_id is renter_id from DB, exposed for business clarity"
        }
