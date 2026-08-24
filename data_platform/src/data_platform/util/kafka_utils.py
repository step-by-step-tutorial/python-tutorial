import logging

logger = logging.getLogger(__name__)


def handle_kafka_response(error, message, event_id: str) -> None:
    if error is not None:
        logger.error(f"Failed to deliver event {event_id} to topic={message.topic()}: {error}")
    else:
        logger.info(f"[asynchronous log] Delivered event {event_id} to topic={message.topic()}")

