from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class OtpCodeBase(BaseModel):
    phone_e164: str


class OtpCodeCreate(OtpCodeBase):
    code_hash: str
    expires_at: datetime


class OtpCodeOut(OtpCodeBase):
    id: UUID
    expires_at: datetime
    attempts: int
    created_at: datetime

    class Config:
        from_attributes = True
 
