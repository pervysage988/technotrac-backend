import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import func

from app.db.base_class import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Who performed the action (linked to User, not Admin directly)
    actor_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # What happened
    action = Column(String, nullable=False)        # e.g. "APPROVE_EQUIPMENT", "VERIFY_KYC"
    entity = Column(String, nullable=False)        # e.g. "Equipment", "Booking"
    entity_id = Column(UUID(as_uuid=True), nullable=True)

    # Optional structured payload for extra context
    payload = Column(JSONB, nullable=True)

    # When
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    actor = relationship("User", back_populates="audit_logs")
