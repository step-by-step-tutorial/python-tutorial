import json
import logging
from functools import partial
from typing import Any

from app_config import env_config as ec
from dataset.definition import Dataset
from connector.messaging import kafka_connector as streamming_connection_factory
from streaming.delivery import topic_on_delivery
from util.file_utils import read_csv_file
from util.string_utils import should_be_not_none

logger = logging.getLogger(__name__)
create_streaming_producer = streamming_connection_factory.create_producer


class CsvPublisher:

    def publish(self, dataset: Dataset) -> int:
        should_be_not_none(dataset.source.file.file_name, "file_name")
        should_be_not_none(dataset.event.key_column, "event_key_column")
        should_be_not_none(dataset.event.converter, "event_converter")
        should_be_not_none(dataset.messaging.topic, "streaming_topic")

        producer = create_streaming_producer()

        event_counter = read_csv_file(
            path_str=dataset.source.file.file_path or str(dataset.source.file.resolve_path(ec.RESOURCES_DIR)),
            consumer=partial(self.publish_row_as_event, dataset=dataset, producer=producer)
        )

        producer.poll(0)
        producer.flush()

        logger.info("Published %s events to streaming topic %s", event_counter, dataset.messaging.topic)

        return event_counter

    @staticmethod
    def publish_row_as_event(row: dict[str, str], dataset: Dataset, producer: Any) -> None:
        event = dataset.event.converter(row)
        event_key = event.get(dataset.event.key_column)

        producer.produce(
            topic=dataset.messaging.topic,
            key=None if event_key is None else str(event_key),
            value=json.dumps(event),
            on_delivery=partial(topic_on_delivery, event_id=event_key)
        )
