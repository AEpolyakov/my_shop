from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.cart.schemas import CartCreateSchema, CartResponseSchema, CartStatusSchema, CartProductAddSchema
from app.cart.service import cart_service
from app.core.session import get_db

cart_router = APIRouter(prefix="/cart", tags=["cart"])


@cart_router.get("/{cart_id}", response_model=CartResponseSchema)
async def get_cart(cart_id: int, db: AsyncSession = Depends(get_db)):
    return await cart_service.get_one(cart_id, db)


@cart_router.post("/", response_model=CartResponseSchema, status_code=status.HTTP_201_CREATED)
async def get_cart(cart: CartCreateSchema, db: AsyncSession = Depends(get_db)):
    return await cart_service.create(cart, db)


@cart_router.delete("/{cart_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart(cart_id: int, db: AsyncSession = Depends(get_db)):
    return await cart_service.delete(db, cart_id)


@cart_router.put("/{cart_id}", response_model=CartResponseSchema)
async def change_cart_status(cart_id: int, cart: CartStatusSchema, db: AsyncSession = Depends(get_db)):
    return await cart_service.update(db, cart_id, cart)


@cart_router.post("/{cart_id}/add_product/", response_model=CartResponseSchema)
async def get_cart(cart_id: int, cart_product: CartProductAddSchema, db: AsyncSession = Depends(get_db)):
    return await cart_service.add_product(cart_id, cart_product, db)
