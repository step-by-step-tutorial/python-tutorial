import json
import logging
from typing import Any

from app_config import env_config as ec
from factory.streamming_connection_factory import create_streaming_producer
from util.streaming_utils import delivery_callback, flush_messages

logger = logging.getLogger(__name__)


class EventProducer:
    def __init__(self) -> None:
        self.producer = create_streaming_producer()

    def publish(self, event: dict[str, Any]) -> None:
        logger.info("Publishing sale event to streaming topic %r", ec.STREAMING_TOPIC)

        self.producer.produce(
            topic=ec.STREAMING_TOPIC,
            key=str(event["order_id"]),
            value=json.dumps(event),
            on_delivery=delivery_callback,
        )
        self.producer.poll(0)

    def flush(self) -> None:
        flush_messages(self.producer)
