import logging

logger = logging.getLogger(__name__)


async def handle_message(message):
    logger.info(f"handling {message=}")
