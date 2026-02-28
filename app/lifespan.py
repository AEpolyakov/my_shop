from contextlib import asynccontextmanager

from aio_pika import connect_robust
from fastapi import FastAPI

from app.config import settings

rabbit_channel = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global rabbit_channel

    rabbit_connection = await connect_robust(
        host=settings.RABBIT_HOST,
        port=settings.RABBIT_PORT,
        login=settings.RABBIT_USER,
        password=settings.RABBIT_PASS,
    )

    rabbit_channel = await rabbit_connection.channel()
    await rabbit_channel.declare_queue(settings.RABBIT_QUEUE, durable=True)

    yield

    await rabbit_connection.close()
