import uuid
from sqlalchemy import Column, String, DateTime, SmallInteger, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base


class OtpCode(Base):
    __tablename__ = "otp_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_e164 = Column(String, index=True, nullable=False)
    code_hash = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    attempts = Column(SmallInteger, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
