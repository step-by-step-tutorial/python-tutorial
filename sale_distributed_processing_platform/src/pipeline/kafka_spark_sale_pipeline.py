import logging
from datetime import UTC, datetime

from itables import show
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.streaming import StreamingQuery

from app_config import env_config as ec
from factory import data_processor_connection_factory
from service import (
    csv_sale_event_service,
    database_sale_service,
    datalake_sale_service,
    datawarehouse_sale_service,
    kafka_sale_service,
    spark_sale_service,
)
from util.datalake_utils import DatalakeLayer, build_sale_datalake_path

logger = logging.getLogger(__name__)


def run() -> None:
    session = data_processor_connection_factory.create_connection()
    ingestion_time = datetime.now(UTC)

    try:
        draw_line()
        logger.info("Starting Kafka Spark sale pipeline with ingestion time %s", ingestion_time)

        publish_sale_events()
        draw_line()

        streaming_query = process_sale_event_stream(session, ingestion_time)
        await_streaming_query(streaming_query)
        draw_line()

        show_pipeline_results(session, ingestion_time)
        draw_line()
    finally:
        stop_session(session)
        draw_line()


def publish_sale_events() -> None:
    logger.info("Publishing sale events from %s to Kafka topic %s", ec.DATA_FILE, ec.KAFKA_TOPIC)
    published_event_count = csv_sale_event_service.publish_sale_events(ec.DATA_FILE)
    logger.info("Published %s sale events", published_event_count)


def process_sale_event_stream(session: SparkSession, ingestion_time: datetime) -> StreamingQuery:
    logger.info("Reading sale events from Kafka topic %s", ec.KAFKA_TOPIC)
    kafka_dataframe = kafka_sale_service.read_sale_event_stream(session)

    logger.info("Parsing Kafka sale events")
    sale_event_dataframe = kafka_sale_service.parse_sale_event_stream(kafka_dataframe)

    logger.info("Starting Spark Structured Streaming query with checkpoint %s", ec.KAFKA_CHECKPOINT_PATH)

    return (
        sale_event_dataframe.writeStream
        .foreachBatch(lambda dataframe, batch_id: process_sale_event_batch(dataframe, batch_id, ingestion_time))
        .option("checkpointLocation", ec.KAFKA_CHECKPOINT_PATH)
        .trigger(availableNow=True)
        .start()
    )


def process_sale_event_batch(dataframe: DataFrame, batch_id: int, ingestion_time: datetime) -> None:
    if dataframe.isEmpty():
        logger.info("Skipping empty Kafka micro-batch %s", batch_id)
        return

    logger.info("Processing Kafka micro-batch %s", batch_id)

    raw_dataframe = dataframe.drop(
        "kafka_topic",
        "kafka_partition",
        "kafka_offset",
        "kafka_timestamp",
    ).persist()

    cleaned_dataframe = spark_sale_service.clean_data(raw_dataframe).persist()
    enriched_dataframe = spark_sale_service.enrich_data(cleaned_dataframe).persist()

    try:
        raw_sale_data_path = build_sale_datalake_path(layer=DatalakeLayer.RAW, ingestion_time=ingestion_time)
        cleaned_sale_data_path = build_sale_datalake_path(layer=DatalakeLayer.CLEANED, ingestion_time=ingestion_time)
        enriched_sale_data_path = build_sale_datalake_path(layer=DatalakeLayer.ENRICHED, ingestion_time=ingestion_time)

        raw_output_dataframe = raw_dataframe.coalesce(1)
        cleaned_output_dataframe = cleaned_dataframe.coalesce(1)
        enriched_output_dataframe = enriched_dataframe.coalesce(1)

        logger.info("Appending raw sale data to %s", raw_sale_data_path)
        datalake_sale_service.append(dataframe=raw_output_dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME,
                                     path=raw_sale_data_path)

        logger.info("Appending cleaned sale data to %s", cleaned_sale_data_path)
        datalake_sale_service.append(dataframe=cleaned_output_dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME,
                                     path=cleaned_sale_data_path)

        logger.info("Appending enriched sale data to %s", enriched_sale_data_path)
        datalake_sale_service.append(dataframe=enriched_output_dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME,
                                     path=enriched_sale_data_path)

        logger.info("Populating database")
        database_sale_service.populate(enriched_dataframe)

        logger.info("Populating datawarehouse")
        datawarehouse_sale_service.populate(enriched_dataframe.toPandas())

        logger.info("Completed Kafka micro-batch %s", batch_id)
    finally:
        enriched_dataframe.unpersist()
        cleaned_dataframe.unpersist()
        raw_dataframe.unpersist()


def await_streaming_query(streaming_query: StreamingQuery) -> None:
    logger.info("Waiting for available Kafka sale events to be processed")
    streaming_query.awaitTermination()
    logger.info("Kafka sale event processing completed")


def show_pipeline_results(session: SparkSession, ingestion_time: datetime) -> None:
    enriched_sale_data_path = build_sale_datalake_path(layer=DatalakeLayer.ENRICHED, ingestion_time=ingestion_time)

    logger.info("Reading enriched sale data from %s", enriched_sale_data_path)
    enriched_dataframe = datalake_sale_service.read(session=session, bucket_name=ec.DATALAKE_BUCKET_NAME,
                                                    path=enriched_sale_data_path)

    logger.info("Showing enriched sale data")
    enriched_dataframe.show(10)

    logger.info("Calculating revenue by category with Spark")
    revenue_by_category_dataframe = spark_sale_service.get_revenue_by_category(enriched_dataframe)
    revenue_by_category_dataframe.show()

    logger.info("Calculating revenue by country with Spark")
    revenue_by_country_dataframe = spark_sale_service.get_revenue_by_country(enriched_dataframe)
    revenue_by_country_dataframe.show()

    logger.info("Calculating revenue by category with Datawarehouse")
    revenue_by_category_datawarehouse_dataframe = datawarehouse_sale_service.get_revenue_by_category()
    show(revenue_by_category_datawarehouse_dataframe)

    logger.info("Calculating revenue by country with Datawarehouse")
    revenue_by_country_datawarehouse_dataframe = datawarehouse_sale_service.get_revenue_by_country()
    show(revenue_by_country_datawarehouse_dataframe)


def stop_session(session: SparkSession) -> None:
    logger.info("Stopping Spark session")
    session.stop()


def draw_line() -> None:
    logger.info(100 * "=")
