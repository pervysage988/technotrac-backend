# app/db/models/misc.py
import uuid
from sqlalchemy import Column, String, Integer
from app.db.base_class import Base


class Misc(Base):
    __tablename__ = "misc"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(String, nullable=True)
