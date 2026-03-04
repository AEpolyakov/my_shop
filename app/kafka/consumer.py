import asyncio
import json
import logging
from typing import Callable

from aiokafka import AIOKafkaConsumer

from app.config import settings

logger = logging.getLogger(__name__)


class KafkaConsumer:
    def __init__(
            self,
            bootstrap_servers: str,
            topic: str,
            group_id: str,
    ):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        self.auto_commit = False
        self.enable_auto_commit = False
        self.consumer: AIOKafkaConsumer = None
        self._task: asyncio.Task | None = None
        self._running = False
        self._message_handler: Callable | None = None

    async def start(self, message_handler: Callable | None = None):
        """Start the Kafka consumer with manual commit"""
        self._message_handler = message_handler

        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            enable_auto_commit=self.enable_auto_commit,  # False = manual commit
            auto_offset_reset='earliest',
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            max_poll_records=10,  # Process 10 messages at a time
            session_timeout_ms=30000,
            heartbeat_interval_ms=10000,
            max_poll_interval_ms=300000,
        )

        await self.consumer.start()
        logger.info(f"Kafka consumer started for topic {self.topic}")

        self._running = True
        self._task = asyncio.create_task(self._consume_loop())


    async def _consume_loop(self):
        """Main consumption loop with manual commit"""
        try:
            async for msg in self.consumer:
                if not self._running:
                    break

                try:
                    logger.info(f"Received message: topic={msg.topic}, "
                                f"partition={msg.partition}, offset={msg.offset}, "
                                f"key={msg.key}")

                    # Process the message
                    if self._message_handler:
                        await self._message_handler(msg)

                    # Manual commit after successful processing
                    await self.consumer.commit()
                    logger.debug(f"Committed offset {msg.offset} for partition {msg.partition}")

                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    # Don't commit on error - message will be re-processed
                    # You could add dead letter queue logic here

        except Exception as e:
            logger.error(f"Error in consume loop: {e}")
        finally:
            logger.info("Consumer loop ended")

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

    async def get_committed_offsets(self):
        """Get current committed offsets for all partitions"""
        if self.consumer:
            return await self.consumer.committed()
        return None

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

kafka_consumer = KafkaConsumer(
    settings.KAFKA_BOOTSTRAP_SERVERS,
    settings.KAFKA_TOPIC,
    settings.KAFKA_CONSUMER_GROUP_ID,
)

def get_kafka_consumer():
    return kafka_consumer