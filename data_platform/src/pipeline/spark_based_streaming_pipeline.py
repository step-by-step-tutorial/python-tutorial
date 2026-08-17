import logging
from datetime import datetime
from typing import cast

from pyspark.sql import DataFrame
from pyspark.sql.streaming import StreamingQuery

from config.app import settings as app_settings
from config.datalake import settings as datalake_settings
from config.messaging import settings as messaging_settings
from config.streaming import settings as streaming_settings
from dataset.definition import DataWarehouseEndpoint, Dataset, FileEndpoint, MessagingEndpoint
from ingestion.file_reader import read_csv_file
from persistence.database import database_service
from persistence.datawarehouse import datawarehouse_service
from presentation.dataframe_display import show
from service.messaging.event_publisher import EventPublisher
from service.spark.batch_service import SparkBatchService as SparkService
from service.spark.runtime import persisted_dataframes
from transformation.conversion.event_mapper import get_event_mapper
from util.log_utils import log_line
from util.path_utils import DatalakeEnv, generate_relative_path
from util.pipeline_utils import create_pipeline_id
from util.time_utils import generate_ingestion_time

logger = logging.getLogger(__name__)


class SparkStreamingPipeline:
    """Hybrid micro-batch pipeline: Kafka ingestion is streamed, downstream loading runs after the stream completes."""

    def __init__(self, ds: Dataset) -> None:
        self.dataset = ds
        self.pipeline_name = "spark_streaming_pipeline"
        self.pipeline_id = create_pipeline_id()
        self.ingestion_time: datetime = generate_ingestion_time()
        self.spark = SparkService()
        self.publisher = EventPublisher()

    def run(self) -> None:
        try:
            logger.info(
                f"Starting ETL pipeline {self.pipeline_name}/{self.pipeline_id} "
                f"with dataset {self.dataset.name} "
                f"at ingestion time {self.ingestion_time.isoformat()}"
            )
            log_line()

            logger.info("step 1")
            self.publish_events()
            log_line()

            logger.info("step 2")
            self.start_batch_storage().awaitTermination()
            log_line()

            enriched_data_path = generate_relative_path(DatalakeEnv.ENRICHED, self.ingestion_time,
                                                        self.dataset.name.lower())

            logger.info("step 3")
            self.populate_database(enriched_data_path)
            log_line()

            logger.info("step 4")
            self.populate_datawarehouse(enriched_data_path)
            log_line()

            logger.info("step 5")
            self.show_dataframe(enriched_data_path)

            logger.info("step 6")
            self.analyzing_via_spark(enriched_data_path)
            log_line()

            logger.info("step 7")
            self.analyzing_via_datawarehouse()
            log_line()

            logger.info(
                f"Finished ETL pipeline {self.pipeline_name}/{self.pipeline_id} "
                f"with dataset {self.dataset.name} "
                f"at ingestion time {self.ingestion_time.isoformat()}"
            )
        finally:
            self.spark.stop()

    def publish_events(self) -> int:
        file_endpoint = cast(FileEndpoint, self.dataset.get_source("file"))
        messaging_endpoint = cast(MessagingEndpoint, self.dataset.get_source("messaging"))
        event_mapper = get_event_mapper(self.dataset.name)
        logger.info(
            "Publishing events from file %s to streaming topic %s",
            file_endpoint.file_name,
            messaging_endpoint.topic
        )

        event_counter = 0

        def collect(row: dict[str, str]) -> None:
            nonlocal event_counter
            self.publisher.publish(messaging_endpoint.topic, event_mapper.map(row))
            event_counter += 1

        read_csv_file(file_endpoint.resolve_path(app_settings.resources_dir), collect)
        self.publisher.flush()
        return event_counter

    def process_stream(self) -> str:
        self.start_batch_storage().awaitTermination()

        return generate_relative_path(DatalakeEnv.ENRICHED, self.ingestion_time, self.dataset.name.lower())

    def start_batch_storage(self) -> StreamingQuery:
        messaging_endpoint = self.dataset.get_source("messaging")
        logger.info("Creating Spark stream for streaming topic %s", messaging_endpoint.topic)

        dataframe = self.spark.read_stream(
            topic=messaging_endpoint.topic,
            bootstrap_servers=messaging_settings.bootstrap_servers,
            starting_offsets=streaming_settings.starting_offsets,
        )

        event_dataframe = self.spark.convert_stream(
            dataframe=dataframe,
            schema=self.dataset.dataframe.schema,
            required_columns=self.dataset.dataframe.required_columns
        )

        logger.info("Starting streaming query with checkpoint location %s", streaming_settings.checkpoint_path)

        return (
            event_dataframe.writeStream
            .foreachBatch(self.store_batch)
            .option("checkpointLocation", streaming_settings.checkpoint_path)
            .trigger(availableNow=True)
            .start()
        )

    def store_batch(self, dataframe: DataFrame, batch_id: int) -> None:
        if dataframe.isEmpty():
            logger.info("Skipping empty Spark micro-batch %s", batch_id)
            return

        logger.info("Processing Spark micro-batch %s", batch_id)

        with persisted_dataframes() as persisted:
            raw_dataframe = dataframe.drop(
                "streaming_topic",
                "streaming_partition",
                "streaming_offset",
                "streaming_timestamp"
            ).persist()

            persisted.append(raw_dataframe)

            raw_relative_path = generate_relative_path(DatalakeEnv.RAW, self.ingestion_time,
                                                       self.dataset.name.lower())

            self.spark.append(
                dataframe=raw_dataframe.coalesce(1),
                bucket_name=datalake_settings.bucket_name,
                path=raw_relative_path,
                scheme=datalake_settings.scheme,
            )

            cleaned_dataframe = self.dataset.get_processor("spark").clean(raw_dataframe).persist()
            persisted.append(cleaned_dataframe)

            cleaned_relative_path = generate_relative_path(DatalakeEnv.CLEANED, self.ingestion_time,
                                                           self.dataset.name.lower())

            self.spark.append(
                dataframe=cleaned_dataframe.coalesce(1),
                bucket_name=datalake_settings.bucket_name,
                path=cleaned_relative_path,
                scheme=datalake_settings.scheme,
            )

            enriched_dataframe = self.dataset.get_processor("spark").enrich(cleaned_dataframe).persist()
            persisted.append(enriched_dataframe)

            enriched_relative_path = generate_relative_path(DatalakeEnv.ENRICHED, self.ingestion_time,
                                                            self.dataset.name.lower())

            self.spark.append(
                dataframe=enriched_dataframe.coalesce(1),
                bucket_name=datalake_settings.bucket_name,
                path=enriched_relative_path,
                scheme=datalake_settings.scheme,
            )

        logger.info("Completed Spark micro-batch %s", batch_id)

    def download_enriched_data(self, relative_path: str) -> DataFrame:
        return self.spark.read(
            bucket_name=datalake_settings.bucket_name,
            path=relative_path,
            scheme=datalake_settings.scheme,
        )

    def populate_database(self, enriched_data_path: str) -> None:
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Populating operational database with enriched data")
        database_service.truncate_and_populate_from_spark(self.dataset, enriched_dataframe)

    def populate_datawarehouse(self, enriched_data_path: str) -> None:
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Populating data warehouse with enriched data")

        datawarehouse_service.truncate_and_populate_from_spark(
            cast(DataWarehouseEndpoint, self.dataset.get_destination("datawarehouse")),
            enriched_dataframe
        )

    def show_dataframe(self, enriched_data_path: str) -> None:
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Displaying enriched data")
        enriched_dataframe.show()
        log_line()

    def analyzing_via_spark(self, enriched_data_path: str) -> None:
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Analyzing enriched data via Spark")

        results = self.dataset.get_processor("spark").analyze(enriched_dataframe)

        for name, dataframe in results.items():
            logger.info("Displaying analysis result %s", name)
            dataframe.show()

    def analyzing_via_datawarehouse(self) -> None:
        results = datawarehouse_service.analyze(
            cast(DataWarehouseEndpoint, self.dataset.get_destination("datawarehouse"))
        )
        logger.info("Analyzing enriched data via data warehouse")

        for dataframe in results.values():
            show(dataframe)
