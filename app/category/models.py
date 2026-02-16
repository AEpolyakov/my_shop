from sqlalchemy import String, Column
from sqlalchemy.orm import relationship

from app.core.models import Base


class Category(Base):
    __tablename__ = "categories"

    name = Column(String(50), unique=True, nullable=False)

    products = relationship("Product", back_populates="category")
