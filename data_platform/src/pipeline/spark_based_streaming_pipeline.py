import logging
from datetime import datetime

from pyspark.sql import DataFrame
from pyspark.sql.streaming import StreamingQuery

from config.datalake import settings as datalake_settings
from config.streaming import settings as streaming_settings
from connector.distributed.spark_service import SparkService
from connector.distributed.spark_runtime import persisted_dataframes
from dataset.definition import Dataset
from ingestion.batch.csv_ingestion import CsvPublisher
from persistence.database import database_service
from persistence.datalake.path_utils import DatalakeLayer, generate_relative_path
from persistence.datawarehouse import datawarehouse_service
from presentation.dataframe_display import show
from presentation.dataframe_display import show_map_of_dataframe
from util.log_utils import log_line
from util.pipeline_utils import create_pipeline_id
from util.time_utils import generate_ingestion_time

logger = logging.getLogger(__name__)


class SparkStreamingPipeline:

    def __init__(self, ds: Dataset) -> None:
        self.dataset = ds
        self.pipeline_name = "spark_streaming_pipeline"
        self.pipeline_id = create_pipeline_id()
        self.ingestion_time: datetime = generate_ingestion_time()
        self.spark = SparkService(ds)
        self.publisher = CsvPublisher()

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

            enriched_data_path = generate_relative_path(DatalakeLayer.ENRICHED, self.ingestion_time,
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
        logger.info(
            "Publishing events from file %s to streaming topic %s",
            self.dataset.source.file.file_name,
            self.dataset.messaging.topic
        )

        return self.publisher.publish(self.dataset)

    def process_stream(self) -> str:
        self.start_batch_storage().awaitTermination()

        return generate_relative_path(DatalakeLayer.ENRICHED, self.ingestion_time, self.dataset.name.lower())

    def start_batch_storage(self) -> StreamingQuery:
        logger.info("Creating Spark stream for streaming topic %s", self.dataset.messaging.topic)

        dataframe = self.spark.read_stream(self.dataset.messaging.topic)

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

            raw_relative_path = generate_relative_path(DatalakeLayer.RAW, self.ingestion_time,
                                                       self.dataset.name.lower())

            self.spark.append(
                dataframe=raw_dataframe.coalesce(1),
                bucket_name=datalake_settings.bucket_name,
                path=raw_relative_path
            )

            cleaned_dataframe = self.dataset.processors["spark"].clean(raw_dataframe).persist()
            persisted.append(cleaned_dataframe)

            cleaned_relative_path = generate_relative_path(DatalakeLayer.CLEANED, self.ingestion_time,
                                                           self.dataset.name.lower())

            self.spark.append(
                dataframe=cleaned_dataframe.coalesce(1),
                bucket_name=datalake_settings.bucket_name,
                path=cleaned_relative_path
            )

            enriched_dataframe = self.dataset.processors["spark"].enrich(cleaned_dataframe).persist()
            persisted.append(enriched_dataframe)

            enriched_relative_path = generate_relative_path(DatalakeLayer.ENRICHED, self.ingestion_time,
                                                            self.dataset.name.lower())

            self.spark.append(
                dataframe=enriched_dataframe.coalesce(1),
                bucket_name=datalake_settings.bucket_name,
                path=enriched_relative_path
            )

        logger.info("Completed Spark micro-batch %s", batch_id)

    def download_enriched_data(self, relative_path: str) -> DataFrame:
        return self.spark.read(
            bucket_name=datalake_settings.bucket_name,
            path=relative_path
        )

    def populate_database(self, enriched_data_path: str) -> None:
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Populating operational database with enriched data")
        database_service.populate(self.dataset, enriched_dataframe)

    def populate_datawarehouse(self, enriched_data_path: str) -> None:
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Populating data warehouse with enriched data")

        datawarehouse_service.truncate_and_populate(
            self.dataset.datawarehouse,
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

        results = self.dataset.processors["spark"].analyze(enriched_dataframe)

        for name, dataframe in results.items():
            logger.info("Displaying analysis result %s", name)
            dataframe.show()

    def analyzing_via_datawarehouse(self) -> None:
        results = datawarehouse_service.analyze(self.dataset.datawarehouse)
        logger.info("Analyzing enriched data via data warehouse")

        for dataframe in results.values():
            show(dataframe)
