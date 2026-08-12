import logging

logger = logging.getLogger(__name__)


def topic_on_delivery(error, message, event_id: str) -> None:
    if error is not None:
        logger.error(f"[asynchronous log] Failed to deliver event {event_id}: {error}")
    elif message is not None:
        logger.info(f"[asynchronous log] Delivered event {event_id} to topic={message.topic()}")
    else:
        logger.error(f"[asynchronous log] Failed to deliver event {event_id}: message is None")
