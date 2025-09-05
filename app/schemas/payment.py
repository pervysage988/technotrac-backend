# app/schemas/payment.py
from pydantic import BaseModel
from uuid import UUID
from enum import Enum
from datetime import datetime


class PaymentMethod(str, Enum):
    UPI = "UPI"
    CASH = "CASH"


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"


class PaymentIntentCreate(BaseModel):
    booking_id: UUID
    method: PaymentMethod


class PaymentIntentOut(BaseModel):
    id: UUID
    booking_id: UUID
    method: PaymentMethod
    status: PaymentStatus
    created_at: datetime
 
