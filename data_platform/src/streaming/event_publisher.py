import json
import logging
from typing import Any

from factory.streamming_connection_factory import create_streaming_producer
from util.streaming_utils import topic_on_delivery

logger = logging.getLogger(__name__)


class EventProducer:

    def __init__(self, topic: str) -> None:
        self.topic = topic
        self.producer = create_streaming_producer()

    def publish(self, event: dict[str, Any], event_key: str | int) -> None:
        logger.info("Publishing event %s to topic %r", event_key, self.topic)

        self.producer.produce(topic=self.topic, key=str(event_key), value=json.dumps(event),on_delivery=topic_on_delivery)
        self.producer.poll(0)
