from __future__ import annotations

import json

import pandas as pd

from dataset.definition import MessagingEndpoint
from connector.kafka_connection_factory import get_connection


class HouseMessageQueueIngestor:
    def __init__(self, endpoint: MessagingEndpoint) -> None:
        self.endpoint = endpoint

    def ingest(self) -> pd.DataFrame:
        consumer = get_connection("house.kafka.listener")
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

        return pd.json_normalize(records)
