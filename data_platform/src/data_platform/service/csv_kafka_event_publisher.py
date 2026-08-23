import json
import logging
from typing import Any

from data_platform.registry.connection_registry import connection_registry
from confluent_kafka import Producer
from data_platform.model import Dataset, FileEndpoint, MessagingEndpoint
from data_platform.converter.event_converter import get_event_converter
from data_platform.util.file_utils import read_csv_file
from data_platform.util.kafka_admin import ensure_topic_exists

logger = logging.getLogger(__name__)


class CsvKafkaEventPublisher:
    def __init__(
        self,
        dataset: Dataset,
        file_endpoint: FileEndpoint,
        messaging_endpoint: MessagingEndpoint,
    ) -> None:
        self.dataset = dataset
        self.file_endpoint = file_endpoint
        self.messaging_endpoint = messaging_endpoint
        self._producer: Producer = connection_registry.get_item(messaging_endpoint.connection_name)
        self._event_mapper = get_event_converter(dataset.name.lower())

    def publish_data(self) -> int:
        ensure_topic_exists(self.messaging_endpoint.bootstrap_servers, self.messaging_endpoint.channel_name)
        logger.info("Reading CSV file from %s", self.file_endpoint.file_path)
        event_counter = read_csv_file(self.file_endpoint.file_path, self.publish_event)
        self._producer.poll(0)
        self._producer.flush()

        logger.info(f"Published {event_counter} CSV rows to streaming topic {self.messaging_endpoint.channel_name}")
        return event_counter

    def publish_event(self, data: dict[str, Any]) -> None:
        event = self._event_mapper.map(data)
        key = None if event.key is None else str(event.key).encode("utf-8")
        value = json.dumps(event.payload, ensure_ascii=False).encode("utf-8")

        self._producer.produce(
            topic=self.messaging_endpoint.channel_name,
            key=key,
            value=value,
        )
