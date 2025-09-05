import uuid 
import enum
from sqlalchemy import (
    Column, String, Enum, Integer, ForeignKey, Boolean,
    DateTime, Float, func, SmallInteger, CheckConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class EquipmentType(str, enum.Enum):
    TRACTOR = "TRACTOR"
    HARVESTER = "HARVESTER"
    SPRAYER = "SPRAYER"
    ROTAVATOR = "ROTAVATOR"
    PLOUGH = "PLOUGH"
    OTHER = "OTHER"


class EquipmentStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    BLOCKED = "BLOCKED"


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    type = Column(Enum(EquipmentType), nullable=False, index=True)
    brand = Column(String, nullable=True)
    model = Column(String, nullable=True)
    daily_rate = Column(Integer, nullable=False)
    hourly_rate = Column(Integer, nullable=True)
    operator_included = Column(Boolean, default=False, index=True)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    status = Column(Enum(EquipmentStatus), default=EquipmentStatus.DRAFT, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    photos = relationship("EquipmentPhoto", back_populates="equipment")
    bookings = relationship("Booking", back_populates="equipment", cascade="all, delete-orphan")
    availabilities = relationship("Availability", back_populates="equipment", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("daily_rate >= 0", name="check_daily_rate_non_negative"),
        CheckConstraint("hourly_rate >= 0", name="check_hourly_rate_non_negative"),
        Index("ix_equipment_type_daily_rate", "type", "daily_rate"),
        Index("ix_equipment_lat_lon", "lat", "lon"),
    )


class EquipmentPhoto(Base):
    __tablename__ = "equipment_photos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_id = Column(UUID(as_uuid=True), ForeignKey("equipment.id"), nullable=False, index=True)
    url = Column(String, nullable=False)
    position = Column(SmallInteger, nullable=True)

    equipment = relationship("Equipment", back_populates="photos")
