from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.kafka.consumer import manage_kafka_consumer
from app.kafka.producer import manage_kafka_producer
from app.rabbit.consumer import manage_rabbit_consumers
from app.rabbit.producer import manage_rabbit_producer


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with manage_kafka_producer(), manage_kafka_consumer(), manage_rabbit_producer(), manage_rabbit_consumers():
        yield
