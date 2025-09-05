# app/schemas/availability.py
from pydantic import BaseModel, validator
from datetime import datetime
from uuid import UUID


class AvailabilityCreate(BaseModel):
    equipment_id: UUID
    start_time: datetime
    end_time: datetime

    @validator("end_time")
    def end_after_start(cls, v, values):
        if "start_time" in values and v <= values["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v


class AvailabilityOut(BaseModel):
    id: UUID
    equipment_id: UUID
    start_time: datetime
    end_time: datetime

    class Config:
        from_attributes = True
