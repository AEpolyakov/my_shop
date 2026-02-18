from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.core.models import Base


class Product(Base):
    __tablename__ = "products"

    name = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False, index=True)

    category_id = Column(ForeignKey("categories.id"), nullable=True)
    category = relationship("Category", back_populates="products")
