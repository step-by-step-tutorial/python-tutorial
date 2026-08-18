from __future__ import annotations

from typing import Any

from connector.spark_session_factory import create_session
from dataset.sale.config import SALE_DATASET
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
    "sale.file.csv": CsvFileIngestor(SALE_DATASET.endpoints["sale.file.csv"]),
    "sale.spark.csv": SparkCsvFileIngestor(create_session()),
    "sale.database": DatabaseIngestor(SALE_DATASET.endpoints["sale.database"]),
    "sale.datawarehouse": DataWarehouseIngestor(SALE_DATASET.endpoints["sale.datawarehouse"]),
    "sale.datalake": DataLakeIngestor(SALE_DATASET.endpoints["sale.datalake"]),
    "sale.spark.datalake": SparkDataLakeIngestor(SALE_DATASET.endpoints["sale.datalake"], create_session()),
    "sale.rest": RestApiIngestor(SALE_DATASET.endpoints["sale.rest"]),
    "sale.kafka.listener": KafkaIngestor(SALE_DATASET.endpoints["sale.kafka.listener"]),
    "sale.spark.kafka": SparkKafkaIngestor(SALE_DATASET.endpoints["sale.kafka.listener"], create_session()),
}


def get_ingestor(name: str) -> Any:
    return registry[name]
