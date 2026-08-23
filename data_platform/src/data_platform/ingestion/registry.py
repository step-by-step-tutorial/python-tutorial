
from typing import Any

from data_platform.connector.spark_session_factory import create_session
from data_platform.model import (
    DataLakeEndpoint,
    DataWarehouseEndpoint,
    DatabaseEndpoint,
    Dataset,
    FileEndpoint,
    MessagingEndpoint,
    RestApiEndpoint,
)
from data_platform.dataset.registry import get_dataset
from data_platform.keys import Key
from data_platform.ingestion.csv_file_ingestor import CsvFileIngestor
from data_platform.ingestion.database_ingestor import DatabaseIngestor
from data_platform.ingestion.datalake_ingestor import DataLakeIngestor
from data_platform.ingestion.datawarehouse_ingestor import DataWarehouseIngestor
from data_platform.ingestion.kafka_ingestor import KafkaIngestor
from data_platform.ingestion.rest_api_ingestor import RestApiIngestor
from data_platform.ingestion.spark_csv_file_ingestor import SparkCsvFileIngestor
from data_platform.ingestion.spark_datalake_ingestor import SparkDataLakeIngestor
from data_platform.ingestion.spark_kafka_ingestor import SparkKafkaIngestor

registry: dict[str, Any] = {}


def _is_session_active(session: Any) -> bool:
    try:
        spark_context = session.sparkContext
        jsc = getattr(spark_context, "_jsc", None)
        return jsc is not None and not jsc.sc().isStopped()
    except Exception:
        return False


def _dataset_for_ingestor(name: str) -> Dataset:
    dataset_name, _, _ = name.partition(".")
    return get_dataset(dataset_name)


def _build_ingestor(dataset: Dataset, name: str) -> Any:
    if name.endswith(".spark.csv"):
        return SparkCsvFileIngestor(create_session())

    if name.endswith(".spark.datalake"):
        endpoint = next(endpoint for endpoint in dataset.endpoints.values() if isinstance(endpoint, DataLakeEndpoint))
        return SparkDataLakeIngestor(endpoint, create_session())

    if name.endswith(".spark.kafka"):
        endpoint = next(endpoint for endpoint in dataset.endpoints.values() if isinstance(endpoint, MessagingEndpoint))
        return SparkKafkaIngestor(endpoint, create_session(), dataset.dataframe.schema)

    endpoint = dataset.endpoints[name]
    if isinstance(endpoint, FileEndpoint):
        return CsvFileIngestor(endpoint)
    if isinstance(endpoint, DatabaseEndpoint):
        return DatabaseIngestor(endpoint)
    if isinstance(endpoint, DataWarehouseEndpoint):
        return DataWarehouseIngestor(endpoint)
    if isinstance(endpoint, DataLakeEndpoint):
        return DataLakeIngestor(endpoint)
    if isinstance(endpoint, MessagingEndpoint):
        return KafkaIngestor(endpoint)
    if isinstance(endpoint, RestApiEndpoint):
        return RestApiIngestor(endpoint)
    raise ValueError(f"Unsupported ingestor endpoint: {name}")


def get_ingestor(name: str) -> Any:
    dataset = _dataset_for_ingestor(name)
    if ".spark." not in name:
        if name not in registry:
            registry[name] = _build_ingestor(dataset, name)
        return registry[name]

    ingestor = registry.get(name)
    session = getattr(ingestor, "session", None)
    if session is not None and _is_session_active(session):
        return ingestor

    ingestor = _build_ingestor(dataset, name)
    registry[name] = ingestor
    return ingestor
