from data_platform.connector.spark_session_factory import create_session
from data_platform.domain.house.dataset import HOUSE_DATASET
from data_platform.ingestion.csv_file_ingestor import CsvFileIngestor
from data_platform.ingestion.data_lake_ingestor import DataLakeIngestor
from data_platform.ingestion.data_warehouse_ingestor import DataWarehouseIngestor
from data_platform.ingestion.database_ingestor import DatabaseIngestor
from data_platform.ingestion.kafka_ingestor import KafkaIngestor
from data_platform.ingestion.spark_csv_file_ingestor import SparkCsvFileIngestor
from data_platform.ingestion.spark_kafka_ingestor import SparkKafkaIngestor
from data_platform.config.keys import Key
from data_platform.model import DataLakeEndpoint, DataWarehouseEndpoint, DatabaseEndpoint, FileEndpoint, \
    MessagingEndpoint
from data_platform.registry.ingestor_registry import ingestor_registry

def register_house_ingestors() -> None:
    if not ingestor_registry.contains(Key.HOUSE_CSV_FILE):
        house_file_csv_ingestor = CsvFileIngestor(HOUSE_DATASET.get_endpoint(Key.HOUSE_CSV_FILE, FileEndpoint))
        ingestor_registry.register(Key.HOUSE_CSV_FILE, house_file_csv_ingestor)
    if not ingestor_registry.contains(Key.HOUSE_KAFKA_CONSUMER):
        house_kafka_listener_ingestor = KafkaIngestor(
            HOUSE_DATASET.get_endpoint(Key.HOUSE_KAFKA_CONSUMER, MessagingEndpoint)
        )
        ingestor_registry.register(Key.HOUSE_KAFKA_CONSUMER, house_kafka_listener_ingestor)
    if not ingestor_registry.contains(Key.HOUSE_KAFKA_PRODUCER):
        house_kafka_producer_ingestor = KafkaIngestor(
            HOUSE_DATASET.get_endpoint(Key.HOUSE_KAFKA_PRODUCER, MessagingEndpoint)
        )
        ingestor_registry.register(Key.HOUSE_KAFKA_PRODUCER, house_kafka_producer_ingestor)
    if not ingestor_registry.contains(Key.HOUSE_DATA_LAKE):
        house_data_lake_ingestor = DataLakeIngestor(HOUSE_DATASET.get_endpoint(Key.HOUSE_DATA_LAKE, DataLakeEndpoint))
        ingestor_registry.register(Key.HOUSE_DATA_LAKE, house_data_lake_ingestor)
    if not ingestor_registry.contains(Key.HOUSE_DATABASE):
        house_database_ingestor = DatabaseIngestor(HOUSE_DATASET.get_endpoint(Key.HOUSE_DATABASE, DatabaseEndpoint))
        ingestor_registry.register(Key.HOUSE_DATABASE, house_database_ingestor)
    if not ingestor_registry.contains(Key.HOUSE_DATA_WAREHOUSE):
        house_data_warehouse_ingestor = DataWarehouseIngestor(
            HOUSE_DATASET.get_endpoint(Key.HOUSE_DATA_WAREHOUSE, DataWarehouseEndpoint)
        )
        ingestor_registry.register(Key.HOUSE_DATA_WAREHOUSE, house_data_warehouse_ingestor)


def register_house_lazy_ingestors() -> None:
    if not ingestor_registry.contains(Key.HOUSE_SPARK_CSV):
        ingestor_registry.register_lazy_item(
            Key.HOUSE_SPARK_CSV,
            lambda: SparkCsvFileIngestor(create_session()),
            cache=False,
        )
    if not ingestor_registry.contains(Key.HOUSE_SPARK_KAFKA):
        ingestor_registry.register_lazy_item(
            Key.HOUSE_SPARK_KAFKA,
            lambda: SparkKafkaIngestor(
                HOUSE_DATASET.get_endpoint(Key.HOUSE_KAFKA_CONSUMER, MessagingEndpoint),
                create_session(),
                HOUSE_DATASET.dataframe.schema,
            ),
            cache=False,
        )
