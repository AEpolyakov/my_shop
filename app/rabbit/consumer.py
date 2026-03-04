import asyncio
import json
from contextlib import asynccontextmanager

from aio_pika import connect_robust
from aio_pika.abc import AbstractRobustConnection, AbstractIncomingMessage

from app.config import settings


class RabbitMQConsumer:
    def __init__(self, url: str, prefetch_count: int) -> None:
        self.url = url
        self.prefetch_count = prefetch_count
        self.connection: AbstractRobustConnection | None = None
        self.channel = None
        self.queue = None
        self.consumer_tag = None

    async def connect(self):
        """Установка соединения с RabbitMQ"""
        try:
            self.connection = await connect_robust(self.url)
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=self.prefetch_count)
            print("Consumer connected to RabbitMQ")
        except Exception as e:
            print(f"Failed to connect to RabbitMQ: {e}")
            raise

    async def close(self):
        """Закрытие соединения"""
        if self.consumer_tag and self.queue:
            await self.queue.cancel(self.consumer_tag)

        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            print("Consumer disconnected from RabbitMQ")

    async def declare_queue(
        self, queue_name: str, durable: bool = True, exclusive: bool = False, auto_delete: bool = False
    ):
        """Объявление очереди для потребления"""
        if not self.channel or self.channel.is_closed:
            await self.connect()

        self.queue = await self.channel.declare_queue(
            name=queue_name, durable=durable, exclusive=exclusive, auto_delete=auto_delete
        )
        print(f"Queue '{queue_name}' declared")
        return self.queue

    async def process_message(self, message: AbstractIncomingMessage):
        """Обработка полученного сообщения"""
        async with message.process():
            try:
                body = message.body.decode()

                try:
                    data = json.loads(body)
                    print(f"Received message: {json.dumps(data, indent=2, ensure_ascii=False)}")
                except json.JSONDecodeError:
                    print(f"Received message (raw): {body}")

            except Exception as e:
                print(f"Error processing message: {e}")
                raise

    async def start_consuming(self, queue_name: str):
        """Начать потребление сообщений из очереди"""
        await self.declare_queue(queue_name)

        self.consumer_tag = await self.queue.consume(self.process_message)
        print(f"Started consuming from queue '{queue_name}'")

        try:
            await asyncio.Future()
        except asyncio.CancelledError:
            print("Consumer stopped")


rabbit_consumer = RabbitMQConsumer(settings.RABBIT_URL, settings.RABBIT_PREFETCH_COUNT)


@asynccontextmanager
async def manage_rabbit_consumers():

    await rabbit_consumer.connect()
    consumer_tasks = [
        asyncio.create_task(rabbit_consumer.start_consuming(settings.RABBIT_QUEUE)),
    ]

    yield

    for task in consumer_tasks:
        task.cancel()
    await asyncio.gather(*consumer_tasks, return_exceptions=True)
    await rabbit_consumer.close()
