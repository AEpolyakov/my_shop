import enum

from pygments.lexer import default
from sqlalchemy import Column, Integer, ForeignKey, Enum, DateTime, func, Float
from sqlalchemy.orm import relationship

from app.core.models import Base

# keep user import !
from app.user.models import User


class CartProduct(Base):
    __tablename__ = "cart_products"

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product = relationship("Product", back_populates="cart_products")

    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    cart = relationship("Cart", back_populates="cart_products")

    quantity = Column(Integer, default=1, nullable=False)

    index = Column(Integer, default=1, nullable=False)

    price = Column(Float, default=0.0, nullable=False)


class CartStatus(enum.Enum):
    draft = "draft"
    processing = "processing"
    complete = "complete"
    declined = "declined"


class Cart(Base):
    __tablename__ = "carts"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="carts")

    status = Column(Enum(CartStatus), default=CartStatus.draft, nullable=False)

    cart_products = relationship("CartProduct", back_populates="cart", cascade="all, delete-orphan")

    @property
    def total_price(self):
        return sum(product.price * product.quantity for product in self.cart_products) if self.cart_products else 0

    @property
    def total_product_count(self):
        return sum(product.quantity for product in self.cart_products)

    @property
    def last_index(self) -> int:
        return max((item.index for item in self.cart_products), default=0)
