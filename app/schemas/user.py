# app/schemas/user.py
import uuid
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


# --- Enums ---
class UserRole(str, Enum):
    FARMER = "FARMER"
    OWNER = "OWNER"
    ADMIN = "ADMIN"


class KycStatus(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"


# --- Farmer Profile Schemas ---
class FarmerProfileBase(BaseModel):
    village: Optional[str] = None
    pincode: Optional[str] = None


class FarmerProfileCreate(FarmerProfileBase):
    pass


class FarmerProfileRead(FarmerProfileBase):
    id: uuid.UUID
    user_id: uuid.UUID

    class Config:
        from_attributes = True


# --- Owner Profile Schemas ---
class OwnerProfileBase(BaseModel):
    upi_id: Optional[str] = None
    kyc_status: KycStatus = KycStatus.UNVERIFIED


class OwnerProfileCreate(OwnerProfileBase):
    pass


class OwnerProfileRead(OwnerProfileBase):
    id: uuid.UUID
    user_id: uuid.UUID

    class Config:
        from_attributes = True


# --- User Schemas ---
class UserBase(BaseModel):
    phone_e164: str
    role: UserRole
    display_name: Optional[str] = None
    language: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: uuid.UUID
    rating_avg: float
    rating_count: int

    class config:
        from_attributes = True
