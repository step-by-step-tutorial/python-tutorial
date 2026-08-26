import json
import logging

from confluent_kafka import Producer

from data_platform.model.endpoints import FileEndpoint, MessagingEndpoint
from data_platform.registry.connection_registry import connection_registry
from data_platform.util.file_utils import read_csv_file
from data_platform.util.kafka_admin import ensure_topic_exists

logger = logging.getLogger(__name__)


class CsvKafkaPublisher:
    def __init__(
            self,
            file_endpoint: FileEndpoint,
            messaging_endpoint: MessagingEndpoint,
    ) -> None:
        self._file_endpoint = file_endpoint
        self._messaging_endpoint = messaging_endpoint
        self._producer: Producer = connection_registry.get_item(messaging_endpoint.connection_name)

    def publish(self) -> int:
        ensure_topic_exists(self._messaging_endpoint.bootstrap_servers, self._messaging_endpoint.channel_name)
        logger.info("Reading CSV file from %s", self._file_endpoint.file_path)
        event_counter = read_csv_file(
            self._file_endpoint.file_path,
            lambda data: self._producer.produce(
                topic=self._messaging_endpoint.channel_name,
                value=json.dumps(data, ensure_ascii=False).encode("utf-8"),
            )
        )
        self._producer.poll(0)
        self._producer.flush()

        logger.info("Published %s CSV rows to streaming topic %s", event_counter, self._messaging_endpoint.channel_name)
        return event_counter
