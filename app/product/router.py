import asyncio
import logging
from typing import Annotated

from fastapi import Body
from fastapi.params import Depends
from sqlalchemy import select, func
from starlette.exceptions import HTTPException

from app.category.models import Category
from app.config import settings
from app.core.router import create_crud_router, CrudRouterTypes
from app.core.session import get_db, AsyncSessionLocal
from app.lifespan import get_rabbit_producer
from app.product.models import Product
from app.product.schemas import ProductsResponseSchema, ProductResponseSchema, ProductCreateSchema, ProductUpdateSchema
from app.product.service import product_service
from app.rabbit.producer import RabbitMQProducer


logger = logging.getLogger(__name__)
product_router = create_crud_router(
    prefix="/products",
    tags=["products"],
    service=product_service,
    types=CrudRouterTypes(ProductCreateSchema, ProductUpdateSchema, ProductResponseSchema, ProductsResponseSchema),
)


@product_router.get("/search")
async def search_product(
        name: str | None = None,
        price: float | None = None,
        category_name: str | None = None,
        db: AsyncSessionLocal = Depends(get_db)):

    def apply_filters(st: select, name: str | None = None, price: float | None = None, category_name: str | None = None):
        if category_name:
            st = st.join(Product.category).where(Category.name.ilike(f"%{category_name}%"))

        if name:
            st = st.where(Product.name.ilike(f"%{name}%"))

        if price:
            st = st.where(Product.price == price)

        return st

    st_results = apply_filters(select(Product), name=name, price=price, category_name=category_name)

    total = await db.scalar(select(func.count()).select_from(st_results.subquery()))
    results = (await db.scalars(st_results.limit(100))).all()

    return {
        'results': results,
        'total': total,
    }

@product_router.post("/send")
async def send_products(producer: RabbitMQProducer = Depends(get_rabbit_producer)):
    try:
        await producer.publish_message(
            message="123",
            routing_key=settings.RABBIT_QUEUE,
        )
        return {"status": "success", "message": f"Task sent to queue", "task_id": 123}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@product_router.post("/send_all")
async def send_products(
    producer: RabbitMQProducer = Depends(get_rabbit_producer), db: AsyncSessionLocal = Depends(get_db)
):
    results = await product_service.get_many(db)
    products = results["results"]

    try:
        await asyncio.gather(
            *[
                producer.publish_message(message=str(product), routing_key=settings.RABBIT_QUEUE)
                for product in products
            ]
        )

        return {"status": "success", "message": f"All products sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@product_router.post("/mass_create")
async def mass_create(
    product_count: Annotated[int, Body()],
    category_count: Annotated[int, Body()],
    db: AsyncSessionLocal = Depends(get_db),
):
    import random
    import string

    characters = string.ascii_letters + string.digits

    def get_random_str():
        return "".join(random.choices(characters, k=16))

    def get_random_id(id_list: list[int]) -> int | None:
        if not id_list:
            return None

        rnd = random.random()
        if rnd < 1 / (len(id_list) + 1):
            return None

        return random.choice(id_list)

    categories_to_create = [Category(name=get_random_str()) for _ in range(category_count)]
    db.add_all(categories_to_create)
    await db.commit()

    s = await db.scalars(select(Category.id))
    category_ids = list(s.all())

    products_to_create = [Product(name=get_random_str(), price=random.random(), category_id=get_random_id(category_ids)) for _ in range(product_count)]

    db.add_all(products_to_create)
    await db.commit()
