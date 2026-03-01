import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.rabbit_consumer import RabbitMQConsumer
from app.rabbit_producer import RabbitMQProducer

rabbit_consumer = RabbitMQConsumer(settings.RABBIT_URL, settings.RABBIT_PREFETCH_COUNT)
rabbit_producer = RabbitMQProducer(settings.RABBIT_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await rabbit_producer.connect()
    await rabbit_consumer.connect()

    consumer_tasks = [
        asyncio.create_task(rabbit_consumer.start_consuming(settings.RABBIT_QUEUE)),
    ]

    yield

    for task in consumer_tasks:
        task.cancel()

    await asyncio.gather(*consumer_tasks, return_exceptions=True)

    await rabbit_producer.close()
    await rabbit_consumer.close()


async def get_rabbit_producer() -> RabbitMQProducer:
    return rabbit_producer
