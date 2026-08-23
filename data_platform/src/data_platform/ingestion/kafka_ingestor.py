import logging

import json

import pandas as pd

from data_platform.model import MessagingEndpoint
from data_platform.registry.connection_registry import connection_registry

logger = logging.getLogger(__name__)


class KafkaIngestor:
    def __init__(self, endpoint: MessagingEndpoint) -> None:
        self.endpoint = endpoint

    def ingest(self) -> pd.DataFrame:
        logger.info("Ingesting messages from Kafka topic %s", self.endpoint.channel_name)
        consumer = connection_registry.get_item(self.endpoint.connection_name)
        consumer.subscribe([self.endpoint.channel_name])

        records: list[dict[str, object]] = []
        try:
            while len(records) < self.endpoint.max_messages:
                message = consumer.poll(self.endpoint.timeout_ms / 1000.0)
                if message is None:
                    break
                if message.error():
                    continue
                payload = message.value()
                if payload is None:
                    continue
                records.append(json.loads(payload.decode("utf-8")))
        finally:
            consumer.close()

        logger.info("Ingested %s Kafka messages from topic %s", len(records), self.endpoint.channel_name)
        return pd.json_normalize(records)
import logging
