import uuid
from sqlalchemy import (
    Column, SmallInteger, Text, ForeignKey,
    DateTime, func, CheckConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    booking_id = Column(
        UUID(as_uuid=True),
        ForeignKey("bookings.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    by_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    for_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    stars = Column(SmallInteger, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    booking = relationship("Booking", back_populates="rating")
    by_user = relationship("User", foreign_keys=[by_user_id])
    for_user = relationship("User", foreign_keys=[for_user_id])

    __table_args__ = (
        CheckConstraint("stars >= 1 AND stars <= 5", name="check_rating_stars"),
        Index("ix_rating_for_user", "for_user_id"),
    )
