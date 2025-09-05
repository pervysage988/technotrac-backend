import uuid 
import enum
from sqlalchemy import (
    Column, Enum, Integer, ForeignKey, DateTime, func, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class BookingStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"


class PaymentMethod(str, enum.Enum):
    CASH = "CASH"
    UPI = "UPI"
    WALLET = "WALLET"


class PaymentStatus(str, enum.Enum):
    NONE = "NONE"
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    equipment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("equipment.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    renter_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    start_ts = Column(DateTime(timezone=True), nullable=False)
    end_ts = Column(DateTime(timezone=True), nullable=False)

    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, index=True)

    price_total = Column(Integer, nullable=False, default=0)
    commission_fee = Column(Integer, nullable=False, default=0)
    owner_payout = Column(Integer, nullable=False, default=0)

    payment_method = Column(Enum(PaymentMethod), nullable=True)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.NONE)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    equipment = relationship("Equipment", back_populates="bookings")
    renter = relationship("User", back_populates="bookings")
    rating = relationship("Rating", back_populates="booking", uselist=False)
    payment = relationship("Payment", back_populates="booking", uselist=False)  # 🔹 NEW

    __table_args__ = (
        Index("ix_booking_equipment", "equipment_id"),
        Index("ix_booking_renter", "renter_id"),
    )
