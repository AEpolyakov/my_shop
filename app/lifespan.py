import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.kafka.consumer import KafkaConsumer
from app.kafka.producer import KafkaProducer
from app.rabbit.consumer import RabbitMQConsumer
from app.rabbit.producer import RabbitMQProducer

rabbit_producer = RabbitMQProducer(settings.RABBIT_URL)
kafka_producer = KafkaProducer(settings.KAFKA_BOOTSTRAP_SERVERS)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def manage_rabbit():
    rabbit_consumer = RabbitMQConsumer(settings.RABBIT_URL, settings.RABBIT_PREFETCH_COUNT)

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


async def handle_message(message):
    logger.info(f"handling {message=}")


@asynccontextmanager
async def manage_kafka():
    await kafka_producer.start()
    kafka_consumer = KafkaConsumer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=settings.KAFKA_CONSUMER_GROUP_ID,
        topic=settings.KAFKA_TOPIC,
    )
    await kafka_consumer.start(message_handler=handle_message)

    yield

    if kafka_consumer:
        await kafka_consumer.stop()

    if kafka_producer:
        await kafka_producer.stop()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with manage_kafka(), manage_rabbit():
        yield


async def get_rabbit_producer() -> RabbitMQProducer:
    return rabbit_producer


async def get_kafka_producer() -> KafkaProducer:
    return kafka_producer
