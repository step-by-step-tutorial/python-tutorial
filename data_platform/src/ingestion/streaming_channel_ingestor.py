from __future__ import annotations

import logging

from pyspark.sql import DataFrame

from connector.session import create_session
from dataset.definition import MessagingEndpoint

logger = logging.getLogger(__name__)


class StreamingChannelIngestor:
    def __init__(self, endpoint: MessagingEndpoint) -> None:
        self.endpoint = endpoint
        self.session = create_session()

    def ingest(self) -> DataFrame:
        logger.info("Reading data from Kafka topic %s", self.endpoint.channel_name)
        return (
            self.session
            .readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", self.endpoint.bootstrap_servers)
            .option("subscribe", self.endpoint.channel_name)
            .option("startingOffsets", self.endpoint.starting_offsets)
            .option("failOnDataLoss", "false")
            .load()
        )
