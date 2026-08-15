from __future__ import annotations

import json
import logging
from collections.abc import Callable
from functools import partial
from typing import Any

from dataset.definition import Dataset
from streaming.delivery import topic_on_delivery
from util.file_utils import read_csv_file
from util.string_utils import should_be_not_none

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

    def publish_row_as_event(self, row: dict[str, str], dataset: Dataset) -> None:
        messaging_endpoint = dataset.get_source("messaging")
        should_be_not_none(dataset.event.key_column, "event_key_column")
        should_be_not_none(dataset.event.converter, "event_converter")
        should_be_not_none(messaging_endpoint.topic, "streaming_topic")

        event = dataset.event.converter(row)
        event_key = event.get(dataset.event.key_column)

        self._get_producer().produce(
            topic=messaging_endpoint.topic,
            key=None if event_key is None else str(event_key),
            value=json.dumps(event),
            on_delivery=partial(topic_on_delivery, event_id=str(event_key)),
        )

    def publish_csv(self, file_path: str, dataset: Dataset) -> int:
        event_counter = read_csv_file(
            path_str=file_path,
            consumer=partial(self.publish_row_as_event, dataset=dataset),
        )
        self.flush()
        logger.info(
            "Published %s events to streaming topic %s",
            event_counter,
            dataset.get_source("messaging").topic,
        )
        return event_counter

    def flush(self) -> None:
        producer = self._get_producer()
        producer.poll(0)
        producer.flush()
