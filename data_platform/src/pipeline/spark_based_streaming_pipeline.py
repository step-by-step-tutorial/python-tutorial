import logging
from datetime import UTC, datetime

from itables import show
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.streaming import StreamingQuery

from app_config import env_config as ec
from app_config.dataframe_schema import SCHEMA
from factory import data_processor_connection_factory
from service import spark_sale_service, spark_streaming_service
from service.database import database_sale_service
from service.datalake import distributed_datalake_service
from service.datawarehouse import datawarehouse_sale_service
from streaming import csv_publisher
from util.datalake_utils import DatalakeLayer, generate_relative_path, persisted_dataframes
from util.log_utils import log_line

logger = logging.getLogger(__name__)


class SparkStreamingPipeline:

    def __init__(self) -> None:
        self.session: SparkSession = data_processor_connection_factory.create_connection()
        self.ingestion_time: datetime = datetime.now(UTC)
        self.run()

    def run(self) -> None:
        try:
            log_line()
            logger.info("Starting pipeline with ingestion time %s", self.ingestion_time)

            logger.info("Publishing events from file %s to streaming topic %s", ec.DATA_FILE, ec.STREAMING_TOPIC)
            csv_publisher.publish(ec.DATA_FILE)
            log_line()

            logger.info("Starting Spark streaming ingestion from streaming to datalake")
            self.start_batch_storage().awaitTermination()
            log_line()

            enriched_dataframe = self.read_enriched_data()

            logger.info("Populating operational database with enriched data")
            database_sale_service.populate(enriched_dataframe)

            logger.info("Populating data warehouse with enriched data")
            datawarehouse_sale_service.populate(enriched_dataframe.toPandas())

            self.show_revenue_by_spark(enriched_dataframe)
            log_line()

            self.show_revenue_by_datawarehouse()
            log_line()

            logger.info("Pipeline completed successfully")
        finally:
            self.stop()

    def start_batch_storage(self) -> StreamingQuery:
        logger.info("Creating Spark stream for streaming topic %s", ec.STREAMING_TOPIC)

        dataframe = spark_streaming_service.read_stream(self.session)
        event_dataframe = spark_streaming_service.convert(dataframe, SCHEMA)

        logger.info("Starting streaming query with checkpoint location %s", ec.STREAMING_CHECKPOINT_PATH)

        return (
            event_dataframe.writeStream
            .foreachBatch(self.store_batch)
            .option("checkpointLocation", ec.STREAMING_CHECKPOINT_PATH)
            .trigger(availableNow=True)
            .start()
        )

    def store_batch(self, dataframe: DataFrame, batch_id: int) -> None:
        if dataframe.isEmpty():
            logger.info("Skipping empty Spark micro-batch %s", batch_id)
            return

        logger.info("Processing Spark micro-batch %s", batch_id)

        with persisted_dataframes() as persisted:
            raw_dataframe = spark_streaming_service.append_raw_data(dataframe, self.ingestion_time).persist()
            persisted.append(raw_dataframe)

            cleaned_dataframe = spark_streaming_service.append_cleaned_data(raw_dataframe, self.ingestion_time).persist()
            persisted.append(cleaned_dataframe)

            enriched_dataframe = spark_streaming_service.append_enriched_data(cleaned_dataframe, self.ingestion_time).persist()
            persisted.append(enriched_dataframe)

        logger.info("Completed Spark micro-batch %s", batch_id)

    def read_enriched_data(self) -> DataFrame:
        path = generate_relative_path(DatalakeLayer.ENRICHED, self.ingestion_time)

        logger.info("Reading enriched data from datalake path %s", path)

        return distributed_datalake_service.read(
            session=self.session,
            bucket_name=ec.DATALAKE_BUCKET_NAME,
            path=path,
        )

    @staticmethod
    def show_revenue_by_spark(dataframe: DataFrame) -> None:
        logger.info("Displaying enriched data sample")
        dataframe.show(10)

        logger.info("Calculating revenue by category using Spark")
        revenue_by_category = spark_sale_service.get_revenue_by_category(dataframe)
        revenue_by_category.show()

        logger.info("Calculating revenue by country using Spark")
        revenue_by_country = spark_sale_service.get_revenue_by_country(dataframe)
        revenue_by_country.show()

    @staticmethod
    def show_revenue_by_datawarehouse() -> None:
        logger.info("Calculating revenue by category using the data warehouse")
        revenue_by_category = datawarehouse_sale_service.get_revenue_by_category()
        show(revenue_by_category)

        logger.info("Calculating revenue by country using the data warehouse")
        revenue_by_country = datawarehouse_sale_service.get_revenue_by_country()
        show(revenue_by_country)

    def stop(self) -> None:
        logger.info("Stopping Spark session")
        self.session.stop()