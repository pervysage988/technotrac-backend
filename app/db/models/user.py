import uuid
import enum
from sqlalchemy import (
    Column,
    String,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    TIMESTAMP,
    func,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class UserRole(str, enum.Enum):
    FARMER = "FARMER"
    OWNER = "OWNER"
    ADMIN = "ADMIN"


class KycStatus(str, enum.Enum):
    UNVERIFIED = "UNVERIFIED"
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_e164 = Column(String, unique=True, index=True, nullable=False)
    role = Column(Enum(UserRole, name="user_role_enum"), index=True, nullable=False)
    display_name = Column(String, nullable=True)
    language = Column(String, nullable=True)  # e.g. "hi", "en", "mr"
    rating_avg = Column(Numeric(2, 1), default=0.0)
    rating_count = Column(Integer, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    bookings = relationship("Booking", back_populates="renter", cascade="all, delete-orphan")
    availabilities = relationship("Availability", back_populates="owner", cascade="all, delete-orphan")
    # inside User class
    audit_logs = relationship("AuditLog", back_populates="actor", cascade="all, delete-orphan")

    owner_profile = relationship(
        "OwnerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    farmer_profile = relationship(
        "FarmerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    # Ratings
    ratings_given = relationship(
        "Rating",
        back_populates="by_user",
        foreign_keys="Rating.by_user_id",
        cascade="all, delete-orphan",
    )
    ratings_received = relationship(
        "Rating",
        back_populates="for_user",
        foreign_keys="Rating.for_user_id",
        cascade="all, delete-orphan",
    )


class OwnerProfile(Base):
    __tablename__ = "owner_profiles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    upi_id = Column(String, nullable=True)
    kyc_status = Column(Enum(KycStatus), default=KycStatus.UNVERIFIED)

    # Relationship
    user = relationship("User", back_populates="owner_profile")


class FarmerProfile(Base):
    __tablename__ = "farmer_profiles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    village = Column(Text, nullable=True)
    pincode = Column(String, index=True)

    # Relationship
    user = relationship("User", back_populates="farmer_profile")


# Explicit indexes (if not covered by Column(index=True))
Index("ix_users_phone_e164", User.phone_e164)
Index("ix_users_role", User.role)
Index("ix_farmer_profiles_pincode", FarmerProfile.pincode)
