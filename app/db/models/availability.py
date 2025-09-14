# app/db/models/availability.py
import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Availability(Base):
    __tablename__ = "availabilities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    equipment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("equipment.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    start_ts = Column(DateTime(timezone=True), nullable=False)
    end_ts = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    equipment = relationship("Equipment", back_populates="availabilities")
    owner = relationship("User", back_populates="availabilities")

    # Keep any multi-column indexes you actually need; single-column indexes are handled by Column(index=True)
    __table_args__ = (
        Index("ix_availability_start_end", "equipment_id", "start_ts", "end_ts"),
    )
