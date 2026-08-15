from __future__ import annotations

import json
import logging
from collections.abc import Callable
from functools import partial
from typing import Any

from streaming.delivery import topic_on_delivery
from transformation.conversion.event_mapper import MappedEvent

logger = logging.getLogger(__name__)


class EventPublisher:
    def __init__(
            self,
            producer: Any | None = None,
            producer_factory: Callable[[], Any] | None = None,
    ) -> None:
        self._producer = producer
        self._producer_factory = producer_factory

    def _get_producer(self) -> Any:
        if self._producer is None:
            if self._producer_factory is None:
                raise ValueError("A producer or producer_factory must be provided.")
            self._producer = self._producer_factory()

        return self._producer

    def publish(self, topic: str, message: MappedEvent) -> None:
        key = None if message.key is None else str(message.key).encode("utf-8")
        value = json.dumps(message.payload, ensure_ascii=False).encode("utf-8")

        self._get_producer().produce(
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
        producer = self._get_producer()
        producer.poll(0)
        producer.flush()
