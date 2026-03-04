import asyncio
import json
from contextlib import asynccontextmanager
from typing import Any

from aio_pika import connect_robust, Message
from aio_pika.abc import AbstractRobustConnection, DeliveryMode
from pydantic import BaseModel

from app.config import settings


class RabbitMQProducer:
    def __init__(self, url: str):
        self.url = url
        self.connection: AbstractRobustConnection | None = None
        self.channel = None

    async def connect(self):
        """Установка соединения с RabbitMQ"""
        print(f"{self.url=}")
        self.connection = await connect_robust(self.url)
        self.channel = await self.connection.channel()
        print("✅ Connected to RabbitMQ")

    async def close(self):
        """Закрытие соединения"""
        if self.connection:
            await self.connection.close()
            print("🔌 Disconnected from RabbitMQ")

    async def publish_message(
        self, message: Any, routing_key: str, exchange_name: str = "", content_type: str = "application/json"
    ):
        """Публикация сообщения в очередь"""
        if not self.channel or self.channel.is_closed:
            await self.connect()

        if isinstance(message, BaseModel):
            message = message.model_dump()

        if isinstance(message, dict):
            message_body = json.dumps(message, default=str).encode()
        else:
            message_body = str(message).encode()

        rabbitmq_message = Message(body=message_body, content_type=content_type, delivery_mode=DeliveryMode.PERSISTENT)

        try:
            if exchange_name:
                exchange = await self.channel.get_exchange(exchange_name)
                await exchange.publish(rabbitmq_message, routing_key=routing_key)
            else:
                await self.channel.default_exchange.publish(rabbitmq_message, routing_key=routing_key)

            print(f"📤 Message published to {routing_key}: {message_body.decode()}")
        except Exception as e:
            print(f"❌ Failed to publish message: {e}")
            raise


rabbit_producer = RabbitMQProducer(settings.RABBIT_URL)


def get_rabbit_producer() -> RabbitMQProducer:
    return rabbit_producer


@asynccontextmanager
async def manage_rabbit_producer():
    await rabbit_producer.connect()
    yield
    await rabbit_producer.close()
