from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.cart.models import Cart, CartProduct
from app.cart.schemas import CartCreateSchema, CartStatusSchema, CartProductAddSchema
from app.core.crud import CRUDBase
from app.product.models import Product


class CartService(CRUDBase[Cart, CartCreateSchema, CartStatusSchema]):

    @property
    def base_select(self) -> Select:
        return select(Cart).options(
            joinedload(Cart.cart_products),
        )

    async def add_product(self, cart_id: int, cart_product: CartProductAddSchema, db: AsyncSession):
        cart = await self.get_one(cart_id, db)
        if not cart:
            self.raise404(cart_id, self.model.__tablename__)

        product = (
            await db.execute(select(Product).where(Product.id == cart_product.product_id and Product.deleted == False))
        ).first()
        if not product:
            self.raise404(cart_id, Product.__tablename__)

        cart_product_orm = (
            await db.execute(
                select(CartProduct).where(
                    CartProduct.product_id == cart_product.product_id and CartProduct.cart_id == cart_id
                )
            )
        ).scalar()
        if not cart_product_orm:
            cart_product_orm = CartProduct(
                **{
                    "product_id": cart_product.product_id,
                    "cart_id": cart_id,
                    "index": cart.last_index + 1,
                }
            )

        cart_product_orm.quantity = cart_product.quantity
        cart_product_orm.price = cart_product.price
        db.add(cart_product_orm)
        await db.commit()
        await db.refresh(cart_product_orm)
        await db.refresh(cart)

        return cart


cart_service = CartService(Cart)
