# app/db/models/misc.py
import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base



class Admin(Base):
    __tablename__ = "admins"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)


class Misc(Base):
    __tablename__ = "misc"

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True)
    value = Column(String)
