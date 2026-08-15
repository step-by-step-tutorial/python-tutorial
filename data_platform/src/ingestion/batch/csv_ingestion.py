import json
import logging
from functools import partial
from typing import Any

from config.app import settings as app_settings
from config.messaging import settings as messaging_settings
from connector.messaging import kafka_connector as streaming_connection_factory
from dataset.definition import Dataset
from streaming.delivery import topic_on_delivery
from util.file_utils import read_csv_file
from util.string_utils import should_be_not_none

logger = logging.getLogger(__name__)
create_streaming_producer = streaming_connection_factory.create_producer


class CsvPublisher:

    def publish(self, dataset: Dataset) -> int:
        file_endpoint = dataset.get_source("file")
        messaging_endpoint = dataset.get_source("messaging")

        should_be_not_none(file_endpoint.file_name, "file_name")
        should_be_not_none(dataset.event.key_column, "event_key_column")
        should_be_not_none(dataset.event.converter, "event_converter")
        should_be_not_none(messaging_endpoint.topic, "streaming_topic")

        producer = create_streaming_producer(messaging_settings.bootstrap_servers)

        event_counter = read_csv_file(
            path_str=file_endpoint.file_path or str(file_endpoint.resolve_path(app_settings.resources_dir)),
            consumer=partial(self.publish_row_as_event, dataset=dataset, producer=producer)
        )

        producer.poll(0)
        producer.flush()

        logger.info("Published %s events to streaming topic %s", event_counter, messaging_endpoint.topic)

        return event_counter

    @staticmethod
    def publish_row_as_event(row: dict[str, str], dataset: Dataset, producer: Any) -> None:
        messaging_endpoint = dataset.get_source("messaging")
        event = dataset.event.converter(row)
        event_key = event.get(dataset.event.key_column)

        producer.produce(
            topic=messaging_endpoint.topic,
            key=None if event_key is None else str(event_key),
            value=json.dumps(event),
            on_delivery=partial(topic_on_delivery, event_id=event_key)
        )
