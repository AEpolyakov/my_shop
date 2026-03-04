import logging

from fastapi import APIRouter, Depends, HTTPException

from app.kafka.consumer import kafka_consumer
from app.kafka.producer import KafkaProducer, get_kafka_producer
from app.kafka.schemas import ConsumerStatus, Message

logger = logging.getLogger(__name__)

kafka_router = APIRouter(
    prefix="/kafka",
)


@kafka_router.post("/send")
async def send_products(message: Message, producer: KafkaProducer = Depends(get_kafka_producer)):
    logger.warning(f'kafka send {message=}')

    try:
        result = await producer.send_message(topic=message.topic, value={"mes": 123123}, key=message.partition_key)

        return {"status": "success", **result}
    except Exception as e:
        # logger.error(f"Failed to send message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")


@kafka_router.get("/consumer/status", response_model=ConsumerStatus)
async def consumer_status():
    """Get consumer status"""

    partitions = []
    if kafka_consumer.consumer:
        assignment = kafka_consumer.consumer.assignment()
        for tp in assignment:
            position = await kafka_consumer.consumer.position(tp)
            committed = await kafka_consumer.consumer.committed(tp)
            partitions.append({
                "topic": tp.topic,
                "partition": tp.partition,
                "current_offset": position,
                "committed_offset": committed
            })

    return ConsumerStatus(
        running=kafka_consumer._running,
        topic=kafka_consumer.topic,
        group_id=kafka_consumer.group_id,
        auto_commit=kafka_consumer.enable_auto_commit,
        partitions=partitions
    )