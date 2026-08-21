import logging

from confluent_kafka import KafkaError, Message

from validation_utils import require_not_blank

logger = logging.getLogger(__name__)


def handle_delivery(error: KafkaError | None, message: Message) -> None:
    if error is not None:
        logger.error(f"Kafka message delivery failed: {error}")
    if message is not None:
        logger.info(
            f"Kafka message {require_not_blank(message.key().decode())} delivered to topic {require_not_blank(message.topic())}"
        )
