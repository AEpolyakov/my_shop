from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.core.session import get_db
from app.kafka.consumer import kafka_consumer
from app.kafka.producer import kafka_producer

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

@health_router.get("/kafka")
async def kafka_health():
    status = {
        "status": "healthy",
        "producer": False,
        "consumer": False,
        "bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS,
    }

    # Check producer
    if kafka_producer and kafka_producer.producer:
        status["producer"] = True

    # Check consumer
    if kafka_consumer and kafka_consumer.consumer:
        status["consumer"] = True
        status["consumer_running"] = kafka_consumer._running

    return status