from __future__ import annotations

from collections.abc import Callable
from typing import Any

from dataset.definition import DataLakeEndpoint, DataWarehouseEndpoint, DatabaseEndpoint, MessagingEndpoint, RestApiEndpoint
from ingestion.database_ingestor import DatabaseIngestor
from ingestion.datalake_ingestor import DataLakeIngestor
from ingestion.datawarehouse_ingestor import DataWarehouseIngestor
from ingestion.message_queue_ingestor import MessageQueueIngestor
from ingestion.rest_api_ingestor import RestApiIngestor
from ingestion.spark_datalake_ingestor import SparkDataLakeIngestor
from ingestion.streaming_channel_ingestor import StreamingChannelIngestor


IngestorFactory = Callable[[Any], Any]


registry: dict[str, IngestorFactory] = {
    "sale.database": lambda endpoint: DatabaseIngestor(endpoint),
    "house.database": lambda endpoint: DatabaseIngestor(endpoint),
    "audit.database": lambda endpoint: DatabaseIngestor(endpoint),
    "sale.datawarehouse": lambda endpoint: DataWarehouseIngestor(endpoint),
    "house.datawarehouse": lambda endpoint: DataWarehouseIngestor(endpoint),
    "audit.datawarehouse": lambda endpoint: DataWarehouseIngestor(endpoint),
    "sale.datalake": lambda endpoint: DataLakeIngestor(endpoint),
    "house.datalake": lambda endpoint: DataLakeIngestor(endpoint),
    "audit.datalake": lambda endpoint: DataLakeIngestor(endpoint),
    "sale_spark_datalake": lambda endpoint: SparkDataLakeIngestor(endpoint),
    "house_spark_datalake": lambda endpoint: SparkDataLakeIngestor(endpoint),
    "audit_spark_datalake": lambda endpoint: SparkDataLakeIngestor(endpoint),
    "sale.rest": lambda endpoint: RestApiIngestor(endpoint),
    "house.rest": lambda endpoint: RestApiIngestor(endpoint),
    "sale.rest.api": lambda endpoint: RestApiIngestor(endpoint),
    "house.rest.api": lambda endpoint: RestApiIngestor(endpoint),
    "sale.kafka.listener": lambda endpoint: StreamingChannelIngestor(endpoint),
    "house.kafka.listener": lambda endpoint: StreamingChannelIngestor(endpoint),
    "audit.kafka.listener": lambda endpoint: StreamingChannelIngestor(endpoint),
    "sale.message.queue": lambda endpoint: MessageQueueIngestor(endpoint),
    "house.message.queue": lambda endpoint: MessageQueueIngestor(endpoint),
    "audit.message.queue": lambda endpoint: MessageQueueIngestor(endpoint),
}


def get_ingestor(name: str, endpoint: Any) -> Any:
    return registry[name](endpoint)
