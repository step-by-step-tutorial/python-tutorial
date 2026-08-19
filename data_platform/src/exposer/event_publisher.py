
import json
import logging
from functools import partial

from confluent_kafka import Producer

from connector.registry import get_connection
from keys import Key
from util.kafka_utils import handle_kafka_response
from transformation.conversion.event_mapper import MappedEvent

logger = logging.getLogger(__name__)


class EventPublisher:
    def __init__(self, producer: Producer | None = None, connection_name: str = Key.SALE_KAFKA_PRODUCER) -> None:
        self._producer = producer or get_connection(connection_name)

    def publish(self, topic: str, message: MappedEvent) -> None:
        key = None if message.key is None else str(message.key).encode("utf-8")
        value = json.dumps(message.payload, ensure_ascii=False).encode("utf-8")

        self._producer.produce(
            topic=topic,
            key=key,
            value=value,
            on_delivery=partial(handle_kafka_response, event_id=str(message.key)),
        )

    def publish_many(self, topic: str, messages: list[MappedEvent] | tuple[MappedEvent, ...]) -> int:
        for message in messages:
            self.publish(topic=topic, message=message)

        self.flush()
        logger.info("Published %s events to streaming topic %s", len(messages), topic)
        return len(messages)

    def flush(self) -> None:
        self._producer.poll(0)
        self._producer.flush()
