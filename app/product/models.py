from sqlalchemy import Column, String, Float

from app.core.models import Base


class Product(Base):
    __tablename__ = "products"

    name = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False, index=True)
