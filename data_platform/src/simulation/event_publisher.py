from __future__ import annotations

import json
import logging
from functools import partial
from typing import Any

from confluent_kafka import Producer

from connector.registry import get_connection
from streaming.delivery import topic_on_delivery
from transformation.conversion.event_mapper import MappedEvent

logger = logging.getLogger(__name__)


class EventPublisher:
    def __init__(self, producer: Producer | None = None, connection_name: str = "sale.kafka.producer") -> None:
        self._producer = producer or get_connection(connection_name)

    def publish(self, topic: str, message: MappedEvent) -> None:
        key = None if message.key is None else str(message.key).encode("utf-8")
        value = json.dumps(message.payload, ensure_ascii=False).encode("utf-8")

        self._producer.produce(
            topic=topic,
            key=key,
            value=value,
            on_delivery=partial(topic_on_delivery, event_id=str(message.key)),
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
