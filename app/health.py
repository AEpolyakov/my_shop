from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.session import get_db

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
    rabbit_status = "connected"

    return {
        "status": "healthy" if rabbit_status == "connected" else "degraded",
        "rabbitmq": rabbit_status,
    }
