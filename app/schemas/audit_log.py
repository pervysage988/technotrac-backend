# app/schemas/audit_log.py
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class AuditLogRead(BaseModel):
    id: UUID
    actor_user_id: UUID | None
    action: str
    entity: str
    entity_id: UUID | None
    payload: dict | None
    created_at: datetime

    class Config:
        from_attributes = True
