from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.cart.models import CartStatus


class CartProductQuantitySchema(BaseModel):
    quantity: int


class CartProductAddSchema(CartProductQuantitySchema):
    product_id: int
    price: float


class CartProductResponseSchema(CartProductQuantitySchema):
    cart_id: int
    index: int
    product_id: int
    price: float


class CartStatusSchema(BaseModel):
    status: CartStatus = CartStatus.draft


class CartCreateSchema(CartStatusSchema):
    user_id: int | None = None


class CartResponseSchema(CartCreateSchema):
    id: int
    status: CartStatus = CartStatus.draft
    created: datetime
    updated: datetime
    cart_products: list[CartProductResponseSchema]
    total_price: float | None = None
    total_product_count: int | None = None

    model_config = ConfigDict(from_attributes=True)
