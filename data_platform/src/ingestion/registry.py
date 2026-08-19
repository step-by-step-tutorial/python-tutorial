from __future__ import annotations

from typing import Any

from connector.spark_session_factory import create_session
from dataset.sale.config import SALE_DATASET
from keys import Key
from ingestion.csv_file_ingestor import CsvFileIngestor
from ingestion.database_ingestor import DatabaseIngestor
from ingestion.datalake_ingestor import DataLakeIngestor
from ingestion.datawarehouse_ingestor import DataWarehouseIngestor
from ingestion.kafka_ingestor import KafkaIngestor
from ingestion.rest_api_ingestor import RestApiIngestor
from ingestion.spark_csv_file_ingestor import SparkCsvFileIngestor
from ingestion.spark_datalake_ingestor import SparkDataLakeIngestor
from ingestion.spark_kafka_ingestor import SparkKafkaIngestor

registry: dict[str, Any] = {
    Key.SALE_FILE_CSV: CsvFileIngestor(SALE_DATASET.endpoints[Key.SALE_FILE_CSV]),
    Key.SALE_DATABASE: DatabaseIngestor(SALE_DATASET.endpoints[Key.SALE_DATABASE]),
    Key.SALE_DATAWAREHOUSE: DataWarehouseIngestor(SALE_DATASET.endpoints[Key.SALE_DATAWAREHOUSE]),
    Key.SALE_DATALAKE: DataLakeIngestor(SALE_DATASET.endpoints[Key.SALE_DATALAKE]),
    Key.SALE_KAFKA_LISTENER: KafkaIngestor(SALE_DATASET.endpoints[Key.SALE_KAFKA_LISTENER]),
    Key.SALE_SPARK_CSV: SparkCsvFileIngestor(create_session()),
    Key.SALE_SPARK_DATALAKE: SparkDataLakeIngestor(SALE_DATASET.endpoints[Key.SALE_DATALAKE], create_session()),
    Key.SALE_SPARK_KAFKA: SparkKafkaIngestor(SALE_DATASET.endpoints[Key.SALE_KAFKA_LISTENER], create_session()),
    Key.SALE_REST: RestApiIngestor(SALE_DATASET.endpoints[Key.SALE_REST]),
}


def get_ingestor(name: str) -> Any:
    return registry[name]
