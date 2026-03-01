import asyncio

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncConnection
from starlette.exceptions import HTTPException

from app.config import settings
from app.core.router import create_crud_router, CrudRouterTypes
from app.core.session import get_db
from app.lifespan import get_rabbit_producer
from app.product.schemas import ProductsResponseSchema, ProductResponseSchema, ProductCreateSchema, ProductUpdateSchema
from app.product.service import product_service
from app.rabbit_producer import RabbitMQProducer

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
