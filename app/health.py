from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.session import get_db
from app.lifespan import rabbit_channel

health_router = APIRouter(prefix="/health")


@health_router.get("/db")
async def db_health(db: Session = Depends(get_db)):
    return {"message": "API is working"}


@health_router.get("/app")
async def app_health():
    return {"status": "ok"}


@health_router.get("/rabbit")
async def rabbit_health():
    """Endpoint для проверки здоровья"""
    rabbit_status = "connected" if (rabbit_channel and not rabbit_channel.is_closed) else "disconnected"

    return {
        "status": "healthy" if rabbit_status == "connected" else "degraded",
        "rabbitmq": rabbit_status,
    }
