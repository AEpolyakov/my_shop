import asyncio
import json
import logging
from typing import Callable

from aiokafka import AIOKafkaConsumer

logger = logging.getLogger(__name__)


class KafkaConsumer:
    def __init__(self, bootstrap_servers: str, group_id: str, topic: str):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.topic = topic
        self.consumer = None
        self._task = None
        self._running = False
        self.message_handler = None

    async def start(self, message_handler: Callable | None = None):
        """Инициализация и запуск consumer"""
        if message_handler:
            self.message_handler = message_handler

        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
        )
        await self.consumer.start()
        logger.info(f"Kafka consumer started for topic: {self.topic}")

        self._running = True
        self._task = asyncio.create_task(self._consume_loop())

    async def stop(self):
        """Остановка consumer"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        if self.consumer:
            await self.consumer.stop()
            logger.info("Kafka consumer stopped")

    async def _consume_loop(self):
        """Основной цикл потребления сообщений"""
        try:
            async for msg in self.consumer:
                if not self._running:
                    break

                logger.info(
                    f"Received message: topic={msg.topic}, partition={msg.partition}, offset={msg.offset}, key={msg.key}"
                )

                if self.message_handler:
                    await self.message_handler(msg.value)
                else:
                    logger.info(f"Message content: {msg.value}")

        except asyncio.CancelledError:
            logger.info("Consumer loop cancelled")
        except Exception as e:
            logger.error(f"Error in consumer loop: {e}")
