from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum
from uuid import UUID


class EquipmentType(str, Enum):
    TRACTOR = "TRACTOR"
    HARVESTER = "HARVESTER"
    SPRAYER = "SPRAYER"
    ROTAVATOR = "ROTAVATOR"
    PLOUGH = "PLOUGH"
    OTHER = "OTHER"


class EquipmentCreate(BaseModel):
    type: EquipmentType

    # ✅ string length limits
    brand: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)

    # ✅ rate validation (strict but reasonable caps)
    daily_rate: int = Field(..., gt=0, le=100_000, description="Daily rental rate in INR")
    hourly_rate: Optional[int] = Field(
        default=None,
        gt=0,
        le=10_000,
        description="Hourly rental rate in INR"
    )

    operator_included: bool = False

    # ✅ geo coords validation
    lat: Optional[float] = Field(None, ge=-90, le=90, description="Latitude in range -90 to 90")
    lon: Optional[float] = Field(None, ge=-180, le=180, description="Longitude in range -180 to 180")

    @validator("hourly_rate")
    def hourly_rate_less_than_daily(cls, v, values):
        """Hourly rate (if given) should not exceed daily rate."""
        if v and "daily_rate" in values and values["daily_rate"] and v > values["daily_rate"]:
            raise ValueError("Hourly rate cannot exceed daily rate")
        return v


class EquipmentOut(EquipmentCreate):
    id: UUID
    status: str

    class Config:
        from_attributes = True
