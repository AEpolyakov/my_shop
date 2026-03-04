import asyncio

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.session import get_db
from app.product.service import product_service
from app.rabbit.producer import RabbitMQProducer, get_rabbit_producer

rabbit_router = APIRouter(prefix="/rabbit")


@rabbit_router.post("/send")
async def send_product(producer: RabbitMQProducer = Depends(get_rabbit_producer)):
    try:
        await producer.publish_message(
            message="123",
            routing_key=settings.RABBIT_QUEUE,
        )
        return {"status": "success", "message": f"Task sent to queue"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@rabbit_router.post("/send_all")
async def send_products(producer: RabbitMQProducer = Depends(get_rabbit_producer), db: AsyncSession = Depends(get_db)):
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
