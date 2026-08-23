
import logging

from pyspark.sql import DataFrame

from data_platform.audit.audit_service import AuditService
from data_platform.config.main_settings import settings as main_settings
from data_platform.connector.spark_session_factory import create_session
from data_platform.model import DataLakeEndpoint, DatabaseEndpoint, DataWarehouseEndpoint, Dataset, FileEndpoint, MessagingEndpoint
from data_platform.service.csv_publisher_service import CsvPublisherService
from data_platform.registry.ingestor_registry import ingestor_registry
from data_platform.keys import Key
from data_platform.persistence.database_repository import DatabaseRepository
from data_platform.persistence.data_warehouse_repository import DataWarehouseRepository
from data_platform.pipeline.batch_pipeline import BatchPipeline
from data_platform.presentation.dataframe_display import show
from data_platform.service.spark_service import SparkService
from data_platform.config.data_lake_environment import DataLakeEnvironment
from data_platform.util.path_utils import generate_relative_path

logger = logging.getLogger(__name__)


class SparkStreamingPipeline(BatchPipeline):
    def __init__(self, ds: Dataset) -> None:
        super().__init__(ds, audit_service=AuditService(ds.audit))
        self.pipeline_name = "spark_streaming_pipeline"
        file_endpoint = self.dataset.get_endpoint(Key.SALE_FILE_CSV, FileEndpoint)
        database_endpoint = self.dataset.get_endpoint(Key.SALE_DATABASE, DatabaseEndpoint)
        datawarehouse_endpoint = self.dataset.get_endpoint(Key.SALE_DATAWAREHOUSE, DataWarehouseEndpoint)
        datalake_endpoint = self.dataset.get_endpoint(Key.SALE_DATALAKE, DataLakeEndpoint)
        producer_endpoint = self.dataset.get_endpoint(Key.SALE_KAFKA_PRODUCER, MessagingEndpoint)
        messaging_endpoint = self.dataset.get_endpoint(Key.SALE_KAFKA_LISTENER, MessagingEndpoint)
        self.csv_publisher = CsvPublisherService(ds, file_endpoint, producer_endpoint)
        self._datalake_endpoint = datalake_endpoint
        self._messaging_endpoint = messaging_endpoint
        self._spark_service: SparkService | None = None
        self.database_repository = DatabaseRepository(database_endpoint)
        self.data_warehouse_repository = DataWarehouseRepository(datawarehouse_endpoint)

    @property
    def spark_service(self) -> SparkService:
        if self._spark_service is None:
            self._spark_service = SparkService(
                create_session(),
                self._datalake_endpoint,
                self._messaging_endpoint,
            )
        return self._spark_service

    def ingest_raw_data(self) -> DataFrame:
        self.csv_publisher.publish_data()
        return ingestor_registry.get_item(Key.SALE_SPARK_KAFKA).ingest()

    def store_raw_data(self, raw_data: DataFrame) -> str:
        relative_path = generate_relative_path(DataLakeEnvironment.RAW, self.ingestion_time, self.dataset.name.lower())

        logger.info("Writing streaming raw data to %s", relative_path)
        self.spark_service.append_stream_to_object_storage(
            dataframe=raw_data,
            path=relative_path,
            checkpoint_path=main_settings.data_lake[Key.DATA_PLATFORM_DATALAKE].checkpoint_path,
        )

        return relative_path

    def clean(self, raw_relative_path: str) -> DataFrame:
        raw_dataframe = self.spark_service.read_from_object_storage(path=raw_relative_path)
        return self.dataset.get_processor("spark").clean(raw_dataframe)

    def store_cleaned_data(self, cleaned_data: DataFrame) -> str:
        relative_path = generate_relative_path(DataLakeEnvironment.CLEANED, self.ingestion_time, self.dataset.name.lower())
        self.spark_service.append_to_object_storage(dataframe=cleaned_data, path=relative_path)
        return relative_path

    def enrich(self, cleaned_relative_path: str) -> DataFrame:
        cleaned_dataframe = self.spark_service.read_from_object_storage(path=cleaned_relative_path)
        return self.dataset.get_processor("spark").enrich(cleaned_dataframe)

    def store_enriched_data(self, enriched_data: DataFrame) -> str:
        relative_path = generate_relative_path(DataLakeEnvironment.ENRICHED, self.ingestion_time, self.dataset.name.lower())
        self.spark_service.append_to_object_storage(dataframe=enriched_data, path=relative_path)
        return relative_path

    def download_enriched_data(self, relative_path: str) -> DataFrame:
        return self.spark_service.read_from_object_storage(path=relative_path)

    def populate_database(self, enriched_data_path: str) -> None:
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Populating operational database with enriched data")
        self.database_repository.truncate_and_populate_from_spark(enriched_dataframe)

    def populate_datawarehouse(self, enriched_data_path: str) -> None:
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Populating data warehouse with enriched data")
        self.data_warehouse_repository.truncate_and_populate_from_spark(enriched_dataframe)

    def analyze_dataframe(self, enriched_data_path: str) -> None:
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Analyzing enriched data via Spark")

        results = self.dataset.get_processor("spark").analyze(enriched_dataframe)

        for name, dataframe in results.items():
            logger.info("Displaying analysis result %s", name)
            dataframe.show()

    def analyze_data_warehouse(self) -> None:
        query_names = [name for name in self.data_warehouse_repository.datawarehouse.query_sql_files.keys() if name != "select_all"]
        results = self.data_warehouse_repository.select_by_queries(query_names)
        logger.info("Analyzing enriched data via data warehouse")

        for dataframe in results.values():
            show(dataframe)

    def show_dataframe(self, enriched_data_path: str) -> None:
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Displaying enriched data")
        enriched_dataframe.show()

    def after_run(self) -> None:
        if self._spark_service is not None:
            self._spark_service.stop()
            self._spark_service = None
