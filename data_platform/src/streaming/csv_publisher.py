import json
import logging
from functools import partial
from typing import Any

from dataset.definition import Dataset
from factory.streamming_connection_factory import create_streaming_producer
from util.file_utils import read_csv_file
from util.streaming_utils import topic_on_delivery
from util.string_utils import should_be_not_none

logger = logging.getLogger(__name__)


class CsvPublisher:

    def publish(self, dataset: Dataset) -> int:
        should_be_not_none(dataset.file_name, "file_name")
        should_be_not_none(dataset.event_key_column, "event_key_column")
        should_be_not_none(dataset.streaming_topic, "streaming_topic")

        producer = create_streaming_producer()

        event_counter = read_csv_file(
            path_str=dataset.file_path,
            consumer=partial(self.publish_row_as_event, dataset=dataset, producer=producer)
        )

        producer.poll(0)
        producer.flush()

        logger.info("Published %s events to streaming topic %s", event_counter, dataset.streaming_topic)

        return event_counter

    @staticmethod
    def publish_row_as_event(row: dict[str, str], dataset: Dataset, producer: Any) -> None:
        event = dataset.event_converter(row)
        event_key = event.get(dataset.event_key_column)

        producer.produce(
            topic=dataset.streaming_topic,
            key=None if event_key is None else str(event_key),
            value=json.dumps(event),
            on_delivery=partial(topic_on_delivery, event_id=event_key)
        )