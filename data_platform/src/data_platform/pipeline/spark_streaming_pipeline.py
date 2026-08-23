import logging

from pyspark.sql import DataFrame

from data_platform.audit.audit_service import AuditService
from data_platform.config.data_lake_environment import DataLakeEnvironment
from data_platform.config.main_settings import settings as main_settings
from data_platform.connector.spark_session_factory import create_session
from data_platform.keys import Key
from data_platform.model import DataLakeEndpoint, DatabaseEndpoint, DataWarehouseEndpoint, Dataset, FileEndpoint, \
    MessagingEndpoint
from data_platform.persistence.spark_data_warehouse_repository import SparkDataWarehouseRepository
from data_platform.persistence.spark_database_repository import SparkDatabaseRepository
from data_platform.persistence.repository_data_populator import RepositoryDataPopulator
from data_platform.pipeline.batch_pipeline import BatchPipeline
from data_platform.service.dataframe_analysis_service import DataFrameAnalyzer
from data_platform.service.data_warehouse_analysis_service import DataWarehouseAnalyzer
from data_platform.presentation.dataframe_display import show_map_of_dataframe, show_spark_dataframes
from data_platform.registry.ingestor_registry import ingestor_registry
from data_platform.registry.connection_registry import connection_registry
from data_platform.registry.event_converter_registry import event_converter_registry
from data_platform.service.csv_kafka_publisher import CsvKafkaPublisher
from data_platform.service.spark_data_lake_service import SparkDataLakeService
from data_platform.service.spark_streaming_service import SparkStreamingService
from data_platform.util.path_utils import generate_relative_path

logger = logging.getLogger(__name__)


class SparkStreamingPipeline(BatchPipeline):
    def __init__(self, ds: Dataset) -> None:
        super().__init__(ds, audit_service=AuditService(ds.audit))
        self.pipeline_name = "spark_streaming_pipeline"
        file_endpoint = self.dataset.get_endpoint(Key(f"{self.dataset.name.lower()}.file.csv"), FileEndpoint)
        database_endpoint = self.dataset.get_endpoint(Key(f"{self.dataset.name.lower()}.database"), DatabaseEndpoint)
        datawarehouse_endpoint = self.dataset.get_endpoint(Key(f"{self.dataset.name.lower()}.datawarehouse"), DataWarehouseEndpoint)
        datalake_endpoint = self.dataset.get_endpoint(Key(f"{self.dataset.name.lower()}.datalake"), DataLakeEndpoint)
        producer_endpoint = self.dataset.get_endpoint(Key(f"{self.dataset.name.lower()}.kafka.producer"), MessagingEndpoint)
        messaging_endpoint = self.dataset.get_endpoint(Key(f"{self.dataset.name.lower()}.kafka.listener"), MessagingEndpoint)
        self._file_endpoint = file_endpoint
        self._producer_endpoint = producer_endpoint
        self._csv_kafka_publisher: CsvKafkaPublisher | None = None
        self._datalake_endpoint = datalake_endpoint
        self._messaging_endpoint = messaging_endpoint
        self._spark_session = None
        self._spark_data_lake_service: SparkDataLakeService | None = None
        self._spark_streaming_service: SparkStreamingService | None = None
        self._database_repository = SparkDatabaseRepository(database_endpoint)
        self._data_warehouse_repository = SparkDataWarehouseRepository(datawarehouse_endpoint)
        self._populators = (
            RepositoryDataPopulator(self.download_enriched_data, self._database_repository.replace),
            RepositoryDataPopulator(self.download_enriched_data, self._data_warehouse_repository.replace),
        )
        self._analyzers = (
            DataFrameAnalyzer(self.download_enriched_data, self.dataset.get_analyzer("spark"), show_spark_dataframes),
            DataWarehouseAnalyzer(
                self._data_warehouse_repository,
                self.dataset.get_analyzer("datawarehouse"),
                show_map_of_dataframe,
            ),
        )

    def before_run(self) -> None:
        self._csv_kafka_publisher = CsvKafkaPublisher(
            self._file_endpoint,
            self._producer_endpoint,
            connection_registry.get_item(self._producer_endpoint.connection_name),
            event_converter_registry.get_item(self.dataset.name),
        )
        self._csv_kafka_publisher.publish()

    def before_task(self) -> None:
        if self._spark_session is not None:
            return
        self._spark_session = create_session()
        self._spark_data_lake_service = SparkDataLakeService(self._spark_session, self._datalake_endpoint)
        self._spark_streaming_service = SparkStreamingService(
            self._spark_session,
            self._messaging_endpoint,
            self._datalake_endpoint,
        )

    def ingest_raw_data(self) -> DataFrame:
        return ingestor_registry.get_item(f"{self.dataset.name.lower()}.spark.kafka").ingest()

    def store_raw_data(self, raw_data: DataFrame) -> str:
        relative_path = generate_relative_path(DataLakeEnvironment.RAW, self.ingestion_time, self.dataset.name.lower())

        logger.info("Writing streaming raw data to %s", relative_path)
        self._spark_streaming_service.save_stream(
            dataframe=raw_data,
            path=relative_path,
            checkpoint_path=main_settings.data_lake[Key.DATA_PLATFORM_DATALAKE].checkpoint_path,
        )

        return relative_path

    def clean(self, raw_relative_path: str) -> DataFrame:
        raw_dataframe = self._spark_data_lake_service.find(path=raw_relative_path)
        return self.dataset.get_transformer("spark").clean(raw_dataframe)

    def store_cleaned_data(self, cleaned_data: DataFrame) -> str:
        relative_path = generate_relative_path(DataLakeEnvironment.CLEANED, self.ingestion_time,
                                               self.dataset.name.lower())
        self._spark_data_lake_service.save(dataframe=cleaned_data, path=relative_path)
        return relative_path

    def enrich(self, cleaned_relative_path: str) -> DataFrame:
        cleaned_dataframe = self._spark_data_lake_service.find(path=cleaned_relative_path)
        return self.dataset.get_transformer("spark").enrich(cleaned_dataframe)

    def store_enriched_data(self, enriched_data: DataFrame) -> str:
        relative_path = generate_relative_path(DataLakeEnvironment.ENRICHED, self.ingestion_time,
                                               self.dataset.name.lower())
        self._spark_data_lake_service.save(dataframe=enriched_data, path=relative_path)
        return relative_path

    def download_enriched_data(self, enriched_data_path: str) -> DataFrame:
        return self._spark_data_lake_service.find(path=enriched_data_path)

    def show_dataframe(self, enriched_data_path: str) -> None:
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Displaying enriched data")
        enriched_dataframe.show()

    def after_run(self) -> None:
        if self._spark_session is not None:
            self._spark_session.stop()
            self._spark_session = None
            self._spark_data_lake_service = None
            self._spark_streaming_service = None
