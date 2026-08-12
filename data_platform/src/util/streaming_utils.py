import logging

logger = logging.getLogger(__name__)


def topic_on_delivery(error, message) -> None:
    if error is not None:
        logger.error("Failed to deliver event: %s", error)
    elif message is not None:
        logger.info(f"Delivered event to topic={message.topic()} partition={message.partition()} offset={message.offset()}")
    else:
        logger.error("Failed to deliver event: message is None")
