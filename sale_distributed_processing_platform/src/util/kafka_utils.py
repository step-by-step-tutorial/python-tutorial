import logging

logger = logging.getLogger(__name__)


def delivery_callback(error, message) -> None:
    if error is not None:
        logger.error("Failed to deliver event: %s", error)
        return

    logger.debug("Delivered event to topic=%s partition=%s offset=%s", message.topic(), message.partition(),
                 message.offset())


def flush_messages(producer) -> None:
    remaining_message_count = producer.flush()
    if remaining_message_count > 0:
        raise RuntimeError(f"Could not publish {remaining_message_count} sale events.")

