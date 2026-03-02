import json
import logging
from typing import Any

from aiokafka import AIOKafkaProducer

logger = logging.getLogger(__name__)


class KafkaProducer:
    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None

    async def start(self):
        """Инициализация и запуск producer"""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers, value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        await self.producer.start()
        logger.info("Kafka producer started")

    async def stop(self):
        """Остановка producer"""
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped")

    async def send_message(self, topic: str, message: str, key: str = None):
        """Отправка сообщения в Kafka"""
        try:
            key_bytes = key.encode("utf-8") if key else None
            logger.info(f"{self.producer=}; {key_bytes=}; {message=}")
            result = await self.producer.send_and_wait(topic=topic, value=message, key=key_bytes)
            logger.info(f"Message sent to {topic}: partition={result.partition}, offset={result.offset}")
            return result
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise
