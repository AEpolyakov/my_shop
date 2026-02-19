from sqlalchemy import Column, Integer, DateTime, func, Boolean
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    id = Column(Integer, primary_key=True, autoincrement=True)
    created = Column(DateTime(timezone=True), default=func.now())
    updated = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    deleted = Column(Boolean, default=False, index=True)
