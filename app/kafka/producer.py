import asyncio
import json
import logging

from aiokafka import AIOKafkaProducer

from app.config import settings

logger = logging.getLogger(__name__)


class KafkaProducer:
    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self.producer: AIOKafkaProducer | None = None
        self._lock = asyncio.Lock()

    async def start(self):
        """Initialize and start the Kafka producer"""
        async with self._lock:
            if self.producer is None:
                self.producer = AIOKafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    client_id="fastapi-producer",
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    key_serializer=lambda k: k.encode('utf-8') if k else None,
                    max_request_size=1048576,  # 1MB
                    acks='all',  # Wait for all replicas to acknowledge
                    retry_backoff_ms=500,
                    request_timeout_ms=40000,
                )
                await self.producer.start()
                logger.info(f"Kafka producer started successfully, connected to {self.bootstrap_servers}")

    async def stop(self):
        """Stop the Kafka producer"""
        async with self._lock:
            if self.producer:
                await self.producer.stop()
                self.producer = None
                logger.info("Kafka producer stopped")

    async def send_message(self, topic: str, value: dict, key: str | None = None):
        """Send a message to Kafka"""

        try:
            # Send message
            future = await self.producer.send(
                topic=topic,
                value=value,
                key=key
            )

            # Wait for the message to be sent
            result = await future

            logger.info(f"Message sent successfully: topic={result.topic}, "
                        f"partition={result.partition}, offset={result.offset}")

            return {
                'topic': result.topic,
                'partition': result.partition,
                'offset': result.offset,
                'timestamp': result.timestamp
            }
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise

kafka_producer = KafkaProducer(settings.KAFKA_BOOTSTRAP_SERVERS)

def get_kafka_producer():
    return kafka_producer