# app/schemas/rating.py
from pydantic import BaseModel, conint
from datetime import datetime
from uuid import UUID


class RatingCreate(BaseModel):
    booking_id: UUID
    stars: conint(ge=1, le=5)   # must be between 1 and 5
    comment: str | None = None


class RatingOut(BaseModel):
    id: UUID
    booking_id: UUID
    by_user_id: UUID
    for_user_id: UUID
    stars: int
    comment: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
 
