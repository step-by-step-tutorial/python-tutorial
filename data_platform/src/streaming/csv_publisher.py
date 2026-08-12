import json
import logging
from functools import partial

from dataset.definition import Dataset
from factory.streamming_connection_factory import create_streaming_producer
from util.file_utils import read_csv_file
from util.streaming_utils import topic_on_delivery
from util.string_utils import should_be_not_none

logger = logging.getLogger(__name__)


class CsvPublisher:

    def __init__(self) -> None:
        self.producer = create_streaming_producer()

    def publish(self, dataset: Dataset) -> int:
        should_be_not_none(dataset.file_name, "file_name")
        should_be_not_none(dataset.event_key_column, "event_key_column")
        should_be_not_none(dataset.streaming_topic, "streaming_topic")

        event_counter = read_csv_file(
            path_str=dataset.file_path,
            consumer=partial(self.publish_row_as_event, dataset=dataset)
        )

        self.producer.poll(0)
        self.producer.flush()

        logger.info("Published %s events to streaming topic %s", event_counter, dataset.streaming_topic)

        return event_counter

    def publish_row_as_event(self, row: dict[str, str], dataset: Dataset) -> None:
        event = dataset.event_converter(row)
        event_key = event[dataset.event_key_column] if dataset.event_key_column in event else None

        self.producer.produce(
            topic=dataset.streaming_topic,
            key=None if event_key is None else str(event_key),
            value=json.dumps(event),
            on_delivery=topic_on_delivery
        )