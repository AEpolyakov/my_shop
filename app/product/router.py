import asyncio
from typing import Annotated

from fastapi import Body
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncConnection
from starlette.exceptions import HTTPException

from app.category.models import Category
from app.category.schemas import CategoryCreateSchema
from app.category.service import category_service
from app.config import settings
from app.core.router import create_crud_router, CrudRouterTypes
from app.core.session import get_db
from app.kafka.message import Message
from app.kafka.producer import KafkaProducer
from app.lifespan import get_rabbit_producer, get_kafka_producer
from app.product.schemas import ProductsResponseSchema, ProductResponseSchema, ProductCreateSchema, ProductUpdateSchema
from app.product.service import product_service
from app.rabbit.producer import RabbitMQProducer

product_router = create_crud_router(
    prefix="/products",
    tags=["products"],
    service=product_service,
    types=CrudRouterTypes(ProductCreateSchema, ProductUpdateSchema, ProductResponseSchema, ProductsResponseSchema),
)


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
    producer: RabbitMQProducer = Depends(get_rabbit_producer), db: AsyncConnection = Depends(get_db)
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


@product_router.post("/kafka_send")
async def send_products(message: Message, producer: KafkaProducer = Depends(get_kafka_producer)):
    if not producer:
        raise HTTPException(status_code=500, detail="Kafka producer not initialized")

    try:
        result = await producer.send_message(topic=message.topic, message="mes: 123123", key=message.partition_key)

        return {"status": "success", "topic": result.topic, "partition": result.partition, "offset": result.offset}
    except Exception as e:
        # logger.error(f"Failed to send message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")


@product_router.post("/mass_create")
async def mass_create(
    product_count: Annotated[int, Body()],
    category_count: Annotated[int, Body()],
    db: AsyncConnection = Depends(get_db),
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

    for i in range(category_count):
        await category_service.create(CategoryCreateSchema(name=get_random_str()), db=db)

    s = await db.scalars(select(Category.id))
    category_ids = list(s.all())

    for i in range(product_count):
        await product_service.create(
            ProductCreateSchema(
                name=get_random_str(),
                price=random.random(),
                category_id=get_random_id(category_ids),
            ),
            db=db,
        )
