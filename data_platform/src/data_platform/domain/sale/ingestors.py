from data_platform.connector.spark_session_factory import create_session
from data_platform.ingestion.csv_file_ingestor import CsvFileIngestor
from data_platform.ingestion.data_lake_ingestor import DataLakeIngestor
from data_platform.ingestion.data_warehouse_ingestor import DataWarehouseIngestor
from data_platform.ingestion.database_ingestor import DatabaseIngestor
from data_platform.ingestion.kafka_ingestor import KafkaIngestor
from data_platform.ingestion.rest_api_ingestor import RestApiIngestor
from data_platform.ingestion.spark_csv_file_ingestor import SparkCsvFileIngestor
from data_platform.ingestion.spark_data_lake_ingestor import SparkDataLakeIngestor
from data_platform.ingestion.spark_kafka_ingestor import SparkKafkaIngestor
from data_platform.config.keys import Key
from data_platform.model import (
    DataLakeEndpoint,
    DataWarehouseEndpoint,
    DatabaseEndpoint,
    FileEndpoint,
    MessagingEndpoint,
    RestApiEndpoint
)
from data_platform.registry.ingestor_registry import ingestor_registry
from data_platform.domain.sale.dataset import SALE_DATASET

def register_sale_ingestors() -> None:
    if not ingestor_registry.contains(Key.SALE_CSV_FILE):
        sale_file_csv_ingestor = CsvFileIngestor(SALE_DATASET.get_endpoint(Key.SALE_CSV_FILE, FileEndpoint))
        ingestor_registry.register(Key.SALE_CSV_FILE, sale_file_csv_ingestor)
    if not ingestor_registry.contains(Key.SALE_REST_API):
        sale_rest_api_ingestor = RestApiIngestor(SALE_DATASET.get_endpoint(Key.SALE_REST_API, RestApiEndpoint))
        ingestor_registry.register(Key.SALE_REST_API, sale_rest_api_ingestor)
    if not ingestor_registry.contains(Key.SALE_KAFKA_CONSUMER):
        sale_kafka_listener_ingestor = KafkaIngestor(
            SALE_DATASET.get_endpoint(Key.SALE_KAFKA_CONSUMER, MessagingEndpoint)
        )
        ingestor_registry.register(Key.SALE_KAFKA_CONSUMER, sale_kafka_listener_ingestor)
    if not ingestor_registry.contains(Key.SALE_KAFKA_PRODUCER):
        sale_kafka_producer_ingestor = KafkaIngestor(
            SALE_DATASET.get_endpoint(Key.SALE_KAFKA_PRODUCER, MessagingEndpoint)
        )
        ingestor_registry.register(Key.SALE_KAFKA_PRODUCER, sale_kafka_producer_ingestor)
    if not ingestor_registry.contains(Key.SALE_DATA_LAKE):
        sale_data_lake_ingestor = DataLakeIngestor(SALE_DATASET.get_endpoint(Key.SALE_DATA_LAKE, DataLakeEndpoint))
        ingestor_registry.register(Key.SALE_DATA_LAKE, sale_data_lake_ingestor)
    if not ingestor_registry.contains(Key.SALE_DATABASE):
        sale_database_ingestor = DatabaseIngestor(SALE_DATASET.get_endpoint(Key.SALE_DATABASE, DatabaseEndpoint))
        ingestor_registry.register(Key.SALE_DATABASE, sale_database_ingestor)
    if not ingestor_registry.contains(Key.SALE_DATA_WAREHOUSE):
        sale_data_warehouse_ingestor = DataWarehouseIngestor(
            SALE_DATASET.get_endpoint(Key.SALE_DATA_WAREHOUSE, DataWarehouseEndpoint)
        )
        ingestor_registry.register(Key.SALE_DATA_WAREHOUSE, sale_data_warehouse_ingestor)


def register_sale_lazy_ingestors() -> None:
    if not ingestor_registry.contains(Key.SALE_SPARK_CSV):
        ingestor_registry.register_lazy_item(
            Key.SALE_SPARK_CSV,
            lambda: SparkCsvFileIngestor(create_session()),
            cache=False,
        )
    if not ingestor_registry.contains(Key.SALE_SPARK_DATA_LAKE):
        ingestor_registry.register_lazy_item(
            Key.SALE_SPARK_DATA_LAKE,
            lambda: SparkDataLakeIngestor(
                SALE_DATASET.get_endpoint(Key.SALE_DATA_LAKE, DataLakeEndpoint),
                create_session(),
            ),
            cache=False,
        )
    if not ingestor_registry.contains(Key.SALE_SPARK_KAFKA):
        ingestor_registry.register_lazy_item(
            Key.SALE_SPARK_KAFKA,
            lambda: SparkKafkaIngestor(
                SALE_DATASET.get_endpoint(Key.SALE_KAFKA_CONSUMER, MessagingEndpoint),
                create_session(),
                SALE_DATASET.dataframe.schema,
            ),
            cache=False,
        )
