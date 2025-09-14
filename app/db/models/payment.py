# app/db/models/payment.py
import uuid
from sqlalchemy import Column, Enum, ForeignKey, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base
import enum


class PaymentMethod(str, enum.Enum):
    UPI = "UPI"
    CASH = "CASH"


class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    method = Column(Enum(PaymentMethod, name="payment_method_enum"), nullable=False)
    status = Column(Enum(PaymentStatus, name="payment_status_enum"), default=PaymentStatus.PENDING, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    booking = relationship("Booking", back_populates="payment")
