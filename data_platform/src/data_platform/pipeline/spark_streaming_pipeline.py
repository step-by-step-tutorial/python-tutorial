import logging

from pyspark.sql import DataFrame

from data_platform.audit.audit_service import AuditService
from data_platform.config.data_lake_environment import DataLakeEnvironment
from data_platform.config.main_settings import settings as main_settings
from data_platform.connector.spark_session_factory import create_session
from data_platform.keys import Key
from data_platform.model import DataLakeEndpoint, DatabaseEndpoint, DataWarehouseEndpoint, Dataset, EndpointRole, FileEndpoint, \
    MessagingEndpoint
from data_platform.persistence.data_warehouse_repository import DataWarehouseRepository
from data_platform.persistence.database_repository import DatabaseRepository
from data_platform.persistence.repository_data_populator import RepositoryDataPopulator
from data_platform.pipeline.batch_pipeline import BatchPipeline
from data_platform.analyzer.dataframe_analyzer import DataFrameAnalyzer
from data_platform.analyzer.data_warehouse_analyzer import DataWarehouseAnalyzer
from data_platform.presentation.dataframe_display import show_map_of_dataframe, show_spark_dataframes
from data_platform.registry.ingestor_registry import ingestor_registry
from data_platform.registry.connection_registry import connection_registry
from data_platform.registry.event_converter_registry import event_converter_registry
from data_platform.service.csv_kafka_event_publisher import CsvKafkaEventPublisher
from data_platform.service.spark_data_lake_service import SparkDataLakeService
from data_platform.service.spark_streaming_service import SparkStreamingService
from data_platform.util.path_utils import generate_relative_path

logger = logging.getLogger(__name__)


class SparkStreamingPipeline(BatchPipeline):
    def __init__(self, ds: Dataset) -> None:
        super().__init__(ds, audit_service=AuditService(ds.audit))
        self.pipeline_name = "spark_streaming_pipeline"
        file_endpoint = self.dataset.get_endpoint_by_role(EndpointRole.FILE_CSV, FileEndpoint)
        database_endpoint = self.dataset.get_endpoint_by_role(EndpointRole.DATABASE, DatabaseEndpoint)
        datawarehouse_endpoint = self.dataset.get_endpoint_by_role(EndpointRole.DATA_WAREHOUSE, DataWarehouseEndpoint)
        datalake_endpoint = self.dataset.get_endpoint_by_role(EndpointRole.DATA_LAKE, DataLakeEndpoint)
        producer_endpoint = self.dataset.get_endpoint_by_role(EndpointRole.KAFKA_PRODUCER, MessagingEndpoint)
        messaging_endpoint = self.dataset.get_endpoint_by_role(EndpointRole.KAFKA_LISTENER, MessagingEndpoint)
        self._file_endpoint = file_endpoint
        self._producer_endpoint = producer_endpoint
        self.csv_kafka_event_publisher: CsvKafkaEventPublisher | None = None
        self._datalake_endpoint = datalake_endpoint
        self._messaging_endpoint = messaging_endpoint
        self._spark_session = None
        self.spark_data_lake_service: SparkDataLakeService | None = None
        self.spark_streaming_service: SparkStreamingService | None = None
        self.database_repository = DatabaseRepository(database_endpoint)
        self.data_warehouse_repository = DataWarehouseRepository(datawarehouse_endpoint)
        self.populators = (
            RepositoryDataPopulator(self.download_enriched_data, self.database_repository.truncate_and_populate_from_spark),
            RepositoryDataPopulator(self.download_enriched_data, self.data_warehouse_repository.truncate_and_populate_from_spark),
        )
        self.analyzers = (
            DataFrameAnalyzer(self.download_enriched_data, self.dataset.get_analyzer("spark"), show_spark_dataframes),
            DataWarehouseAnalyzer(
                self.data_warehouse_repository.select_by_queries,
                [name for name in self.data_warehouse_repository.datawarehouse.query_sql_files if name != "select_all"],
                show_map_of_dataframe,
            ),
        )

    def before_run(self) -> None:
        self._spark_session = create_session()
        self.spark_data_lake_service = SparkDataLakeService(self._spark_session, self._datalake_endpoint)
        self.spark_streaming_service = SparkStreamingService(
            self._spark_session,
            self._messaging_endpoint,
            self._datalake_endpoint,
        )
        self.csv_kafka_event_publisher = CsvKafkaEventPublisher(
            self._file_endpoint,
            self._producer_endpoint,
            connection_registry.get_item(self._producer_endpoint.connection_name),
            event_converter_registry.get_item(self.dataset.name),
        )
        self.csv_kafka_event_publisher.publish_data()

    def ingest_raw_data(self) -> DataFrame:
        return ingestor_registry.get_item(f"{self.dataset.name.lower()}.spark.kafka").ingest()

    def store_raw_data(self, raw_data: DataFrame) -> str:
        relative_path = generate_relative_path(DataLakeEnvironment.RAW, self.ingestion_time, self.dataset.name.lower())

        logger.info("Writing streaming raw data to %s", relative_path)
        self.spark_streaming_service.append_stream_to_object_storage(
            dataframe=raw_data,
            path=relative_path,
            checkpoint_path=main_settings.data_lake[Key.DATA_PLATFORM_DATALAKE].checkpoint_path,
        )

        return relative_path

    def clean(self, raw_relative_path: str) -> DataFrame:
        raw_dataframe = self.spark_data_lake_service.read_from_object_storage(path=raw_relative_path)
        return self.dataset.get_transformer("spark").clean(raw_dataframe)

    def store_cleaned_data(self, cleaned_data: DataFrame) -> str:
        relative_path = generate_relative_path(DataLakeEnvironment.CLEANED, self.ingestion_time,
                                               self.dataset.name.lower())
        self.spark_data_lake_service.append_to_object_storage(dataframe=cleaned_data, path=relative_path)
        return relative_path

    def enrich(self, cleaned_relative_path: str) -> DataFrame:
        cleaned_dataframe = self.spark_data_lake_service.read_from_object_storage(path=cleaned_relative_path)
        return self.dataset.get_transformer("spark").enrich(cleaned_dataframe)

    def store_enriched_data(self, enriched_data: DataFrame) -> str:
        relative_path = generate_relative_path(DataLakeEnvironment.ENRICHED, self.ingestion_time,
                                               self.dataset.name.lower())
        self.spark_data_lake_service.append_to_object_storage(dataframe=enriched_data, path=relative_path)
        return relative_path

    def download_enriched_data(self, relative_path: str) -> DataFrame:
        return self.spark_data_lake_service.read_from_object_storage(path=relative_path)

    def show_dataframe(self, enriched_data_path: str) -> None:
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Displaying enriched data")
        enriched_dataframe.show()

    def after_run(self) -> None:
        if self._spark_session is not None:
            self._spark_session.stop()
            self._spark_session = None
            self.spark_data_lake_service = None
            self.spark_streaming_service = None
