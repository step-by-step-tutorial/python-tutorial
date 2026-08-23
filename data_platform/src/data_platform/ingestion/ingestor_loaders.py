from typing import Any

from data_platform.connector.spark_session_factory import create_session
from data_platform.dataset.house_config import HOUSE_DATASET
from data_platform.dataset.sale_config import SALE_DATASET
from data_platform.ingestion.csv_file_ingestor import CsvFileIngestor
from data_platform.ingestion.data_lake_ingestor import DataLakeIngestor
from data_platform.ingestion.data_warehouse_ingestor import DataWarehouseIngestor
from data_platform.ingestion.database_ingestor import DatabaseIngestor
from data_platform.ingestion.kafka_ingestor import KafkaIngestor
from data_platform.ingestion.rest_api_ingestor import RestApiIngestor
from data_platform.ingestion.spark_csv_file_ingestor import SparkCsvFileIngestor
from data_platform.ingestion.spark_data_lake_ingestor import SparkDataLakeIngestor
from data_platform.ingestion.spark_kafka_ingestor import SparkKafkaIngestor
from data_platform.keys import Key
from data_platform.model import DataLakeEndpoint, DataWarehouseEndpoint, DatabaseEndpoint, FileEndpoint, MessagingEndpoint, RestApiEndpoint


def load_sale_file_csv() -> Any:
    return CsvFileIngestor(SALE_DATASET.get_endpoint(Key.SALE_FILE_CSV, FileEndpoint))


def load_sale_rest_api() -> Any:
    return RestApiIngestor(SALE_DATASET.get_endpoint(Key.SALE_REST, RestApiEndpoint))


def load_sale_kafka_listener() -> Any:
    return KafkaIngestor(SALE_DATASET.get_endpoint(Key.SALE_KAFKA_LISTENER, MessagingEndpoint))


def load_sale_kafka_producer() -> Any:
    return KafkaIngestor(SALE_DATASET.get_endpoint(Key.SALE_KAFKA_PRODUCER, MessagingEndpoint))


def load_sale_data_lake() -> Any:
    return DataLakeIngestor(SALE_DATASET.get_endpoint(Key.SALE_DATALAKE, DataLakeEndpoint))


def load_sale_database() -> Any:
    return DatabaseIngestor(SALE_DATASET.get_endpoint(Key.SALE_DATABASE, DatabaseEndpoint))


def load_sale_data_warehouse() -> Any:
    return DataWarehouseIngestor(SALE_DATASET.get_endpoint(Key.SALE_DATAWAREHOUSE, DataWarehouseEndpoint))


def load_house_file_csv() -> Any:
    return CsvFileIngestor(HOUSE_DATASET.get_endpoint(Key.HOUSE_FILE_CSV, FileEndpoint))


def load_house_kafka_listener() -> Any:
    return KafkaIngestor(HOUSE_DATASET.get_endpoint(Key.HOUSE_KAFKA_LISTENER, MessagingEndpoint))


def load_house_kafka_producer() -> Any:
    return KafkaIngestor(HOUSE_DATASET.get_endpoint(Key.HOUSE_KAFKA_PRODUCER, MessagingEndpoint))


def load_house_data_lake() -> Any:
    return DataLakeIngestor(HOUSE_DATASET.get_endpoint(Key.HOUSE_DATALAKE, DataLakeEndpoint))


def load_house_database() -> Any:
    return DatabaseIngestor(HOUSE_DATASET.get_endpoint(Key.HOUSE_DATABASE, DatabaseEndpoint))


def load_house_data_warehouse() -> Any:
    return DataWarehouseIngestor(HOUSE_DATASET.get_endpoint(Key.HOUSE_DATAWAREHOUSE, DataWarehouseEndpoint))


def load_sale_spark_csv() -> Any:
    return SparkCsvFileIngestor(create_session())


def load_sale_spark_data_lake() -> Any:
    return SparkDataLakeIngestor(
        SALE_DATASET.get_endpoint(Key.SALE_DATALAKE, DataLakeEndpoint),
        create_session(),
    )


def load_sale_spark_kafka() -> Any:
    return SparkKafkaIngestor(
        SALE_DATASET.get_endpoint(Key.SALE_KAFKA_LISTENER, MessagingEndpoint),
        create_session(),
        SALE_DATASET.dataframe.schema,
    )
