import logging
from pathlib import Path

from pyspark.sql import DataFrame

from audit.audit_service import AuditService
from connector.spark_session_factory import create_session
from dataset.definition import DataLakeEndpoint, DatabaseEndpoint, Dataset, DataWarehouseEndpoint, FileEndpoint, \
    MessagingEndpoint
from ingestion.registry import get_ingestor
from keys import Key
from persistence.database_repository import DatabaseRepository
from persistence.datawarehouse_repository import DataWarehouseRepository
from pipeline.batch_pipeline import BatchPipeline
from presentation.dataframe_display import show
from service.spark_service import SparkService
from util.path_utils import DatalakeEnv, generate_relative_path

logger = logging.getLogger(__name__)


class SparkPipeline(BatchPipeline):

    def __init__(self, ds: Dataset) -> None:
        super().__init__(ds, audit_service=AuditService(ds.audit))
        self.pipeline_name = "spark_pipeline"
        file_endpoint = self.dataset.get_endpoint(Key.SALE_FILE_CSV, FileEndpoint)
        database_endpoint = self.dataset.get_endpoint(Key.SALE_DATABASE, DatabaseEndpoint)
        datawarehouse_endpoint = self.dataset.get_endpoint(Key.SALE_DATAWAREHOUSE, DataWarehouseEndpoint)
        datalake_endpoint = self.dataset.get_endpoint(Key.SALE_DATALAKE, DataLakeEndpoint)
        messaging_endpoint = self.dataset.get_endpoint(Key.SALE_KAFKA_LISTENER, MessagingEndpoint)
        self._datalake_endpoint = datalake_endpoint
        self._messaging_endpoint = messaging_endpoint
        self._spark_service: SparkService | None = None
        self.database_repository = DatabaseRepository(database_endpoint)
        self.datawarehouse_repository = DataWarehouseRepository(datawarehouse_endpoint)
        self.file_path = Path(file_endpoint.file_path)

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
        return get_ingestor(Key.SALE_SPARK_CSV).ingest(self.file_path, self.dataset.dataframe.schema)

    def store_raw_data(self, raw_data: DataFrame) -> str:
        relative_path = generate_relative_path(DatalakeEnv.RAW, self.ingestion_time, self.dataset.name.lower())
        self.spark_service.overwrite_to_object_storage(dataframe=raw_data, path=relative_path)
        return relative_path

    def cleaning(self, raw_relative_path: str) -> DataFrame:
        raw_dataframe = self.spark_service.read_from_object_storage(path=raw_relative_path)
        return self.dataset.get_processor("spark").clean(raw_dataframe)

    def store_cleaned_data(self, cleaned_data: DataFrame) -> str:
        relative_path = generate_relative_path(DatalakeEnv.CLEANED, self.ingestion_time, self.dataset.name.lower())
        self.spark_service.append_to_object_storage(dataframe=cleaned_data, path=relative_path)
        return relative_path

    def enriching(self, cleaned_relative_path: str) -> DataFrame:
        cleaned_dataframe = self.spark_service.read_from_object_storage(path=cleaned_relative_path)
        return self.dataset.get_processor("spark").enrich(cleaned_dataframe)

    def store_enriched_data(self, enriched_data: DataFrame) -> str:
        relative_path = generate_relative_path(DatalakeEnv.ENRICHED, self.ingestion_time, self.dataset.name.lower())
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
        self.datawarehouse_repository.truncate_and_populate_from_spark(enriched_dataframe)

    def analyze_via_dataframe(self, enriched_data_path: str) -> None:
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Analyzing enriched data via Spark")
        results = self.dataset.get_processor("spark").analyze(enriched_dataframe)
        for name, dataframe in results.items():
            logger.info("Displaying analysis result %s", name)
            dataframe.show()

    def analyzing_via_datawarehouse(self) -> None:
        query_names = [name for name in self.datawarehouse_repository.datawarehouse.query_sql_files.keys() if name != "select_all"]
        results = self.datawarehouse_repository.select_by_queries(query_names)
        logger.info("Analyzing enriched data via data warehouse")
        for dataframe in results.values():
            show(dataframe)

    def show_dataframe(self, enriched_data_path: str) -> None:
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Displaying enriched data")
        enriched_dataframe.show()
        return None

    def after_run(self) -> None:
        if self._spark_service is not None:
            self._spark_service.stop()
            self._spark_service = None
