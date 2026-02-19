from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.core.models import Base


class User(Base):
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)

    carts = relationship("Cart", back_populates="user")
