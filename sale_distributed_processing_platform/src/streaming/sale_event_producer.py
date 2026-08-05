import json
import logging
from collections.abc import Callable
from typing import Any

from confluent_kafka import Message, Producer

from app_config import env_config as ec

logger = logging.getLogger(__name__)


class SaleEventProducer:
    def __init__(self) -> None:
        self.producer = Producer({"bootstrap.servers": ec.KAFKA_BOOTSTRAP_SERVERS})

    def publish_sale_event(self, sale_event: dict[str, Any]) -> None:
        self.producer.produce(
            topic=ec.KAFKA_TOPIC,
            key=str(sale_event["order_id"]),
            value=json.dumps(sale_event),
            on_delivery=self._handle_delivery,
        )
        self.producer.poll(0)

    def flush(self) -> None:
        remaining_message_count = self.producer.flush()

        if remaining_message_count > 0:
            raise RuntimeError(f"Could not publish {remaining_message_count} sale events.")

    @staticmethod
    def _handle_delivery(error: Exception | None, message: Message) -> None:
        if error is not None:
            logger.error("Failed to publish sale event: %s", error)
            return

        logger.debug(
            "Published sale event to topic=%s partition=%s offset=%s",
            message.topic(), message.partition(), message.offset()
        )
