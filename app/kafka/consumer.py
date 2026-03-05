import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Callable

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer, ConsumerRecord

from app.config import settings
from app.kafka.consume_handlers import handle_message

logger = logging.getLogger(__name__)


class KafkaConsumeError(Exception):
    pass


class KafkaConsumer:
    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
        group_id: str,
        message_handler: Callable,
        max_retries: int = 3,
    ):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        self.auto_commit = False
        self.enable_auto_commit = False
        self.consumer: AIOKafkaConsumer = None
        self._task: asyncio.Task | None = None
        self._running = False
        self._message_handler: Callable = message_handler
        self.dlq_topic = f"{topic}-dlq"
        self.max_retries = max_retries
        self.retry_backoff_s = 2
        self.producer: AIOKafkaProducer = None

    async def start(self):
        """Start the Kafka consumer with manual commit"""

        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            enable_auto_commit=self.enable_auto_commit,  # False = manual commit
            auto_offset_reset="earliest",
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            key_deserializer=lambda k: k.decode("utf-8") if k else None,
            session_timeout_ms=30000,
            heartbeat_interval_ms=10000,
            max_poll_interval_ms=300000,
        )

        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers, value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )

        await self.consumer.start()
        await self.producer.start()
        logger.info(f"Kafka consumer started for topic {self.topic}")

        self._running = True
        self._task = asyncio.create_task(self._consume_loop())

    async def process_with_retry(self, message: ConsumerRecord, handle_fn: Callable):
        """Process message with retry logic"""

        retries = 0
        message_value = message.value

        while retries < self.max_retries:

            try:
                success = await handle_fn(message_value)

                if success:
                    await self.consumer.commit()
                    logger.info(f"Message successfully processed {message_value}")

                    return True
                else:
                    raise KafkaConsumeError

            except Exception as e:
                retries += 1
                logger.error(f"Error processing message: {e}, retries {retries}/{self.max_retries}")

                if retries < self.max_retries:
                    wait_time = self.retry_backoff_s * retries
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Max retries ({self.max_retries}) exhausted")
                    await self.send_to_dlq(message, e)
                    await self.consumer.commit()
                    return False

    async def _consume_loop(self):
        """Main consumption loop with manual commit"""

        try:
            async for message in self.consumer:
                if not self._running:
                    break

                logger.info(
                    f"Received message: topic={message.topic}, "
                    f"partition={message.partition}, offset={message.offset}, "
                    f"key={message.key}"
                )

                await self.process_with_retry(message, handle_fn=self._message_handler)

        except Exception as e:
            logger.error(f"Error in consume loop: {e}")
        finally:
            logger.info("Consumer loop ended")
            await self.cleanup()

    async def cleanup(self):
        """Очистка ресурсов"""
        self.running = False
        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()
        logger.info("Consumer и Producer остановлены")

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

    async def commit_specific_offset(self, topic: str, partition: int, offset: int):
        """Manually commit a specific offset"""
        if self.consumer:
            await self.consumer.commit({(topic, partition): offset})
            logger.info(f"Committed specific offset: {topic}:{partition}:{offset}")

    async def seek_to_offset(self, topic: str, partition: int, offset: int):
        """Seek to a specific offset"""
        if self.consumer:
            tp = self.consumer.assignment()
            if tp:
                await self.consumer.seek(tp[0], offset)
                logger.info(f"Seeked to offset {offset}")

    async def pause(self):
        """Pause consumption"""
        if self.consumer:
            self.consumer.pause()
            logger.info("Consumer paused")

    async def resume(self):
        """Resume consumption"""
        if self.consumer:
            self.consumer.resume()
            logger.info("Consumer resumed")

    async def send_to_dlq(self, message: ConsumerRecord, error: Exception):
        """Send failed message to DLQ with error details"""

        try:
            failed_message = {
                "original_message": message.value,
                "error_info": {
                    "topic": message.topic,
                    "partition": message.partition,
                    "offset": message.offset,
                    "timestamp": message.timestamp,
                    "error": str(error),
                },
            }

            await self.producer.send(
                self.dlq_topic,
                failed_message,
            )
            await self.producer.flush()
            logger.info(f"Сообщение отправлено в DLQ: {self.dlq_topic}")

        except Exception as e:
            logger.error(f"Failed to send message to DLQ: {e}", exc_info=True)


kafka_consumer = KafkaConsumer(
    settings.KAFKA_BOOTSTRAP_SERVERS,
    settings.KAFKA_TOPIC,
    settings.KAFKA_CONSUMER_GROUP_ID,
    handle_message,
)


def get_kafka_consumer():
    return kafka_consumer


@asynccontextmanager
async def manage_kafka_consumer():
    await kafka_consumer.start()
    yield
    await kafka_consumer.stop()
