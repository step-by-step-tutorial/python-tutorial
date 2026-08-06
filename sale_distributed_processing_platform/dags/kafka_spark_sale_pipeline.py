import logging
from datetime import UTC, datetime, timedelta

import pendulum
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.streaming import StreamingQuery

from app_config import env_config as ec
from factory import data_processor_connection_factory
from service import (
    kafka_spark_sale_service,
    spark_sale_service,
)
from service.datawarehouse import datawarehouse_sale_service
from service.database import database_sale_service
from service.datalake import datalake_spark_sale_service
from streaming import csv_sale_publisher
from util.datalake_utils import DatalakeLayer, build_sale_datalake_path

logger = logging.getLogger(__name__)

DAG_ID = "kafka_spark_sale_pipeline"
DAG_START_DATE = pendulum.datetime(2026, 1, 1, tz="UTC")


def create_ingestion_time() -> str:
    ingestion_time = datetime.now(UTC)

    logger.info("Created ingestion time %s", ingestion_time)

    return ingestion_time.isoformat()


def publish_sale_events() -> None:
    draw_line()

    logger.info("Publishing sale events from %s to Kafka topic %s", ec.DATA_FILE, ec.KAFKA_TOPIC)

    published_event_count = csv_sale_publisher.publish_data(ec.DATA_FILE)

    logger.info("Published %s sale events to Kafka topic %s", published_event_count, ec.KAFKA_TOPIC)

    draw_line()


def process_sale_event_stream(ingestion_time: str) -> None:
    session = data_processor_connection_factory.create_connection()
    parsed_ingestion_time = datetime.fromisoformat(ingestion_time)

    try:
        draw_line()

        logger.info("Starting Kafka Spark sale processing with ingestion time %s", parsed_ingestion_time)

        streaming_query = start_sale_event_stream(session=session, ingestion_time=parsed_ingestion_time)
        await_streaming_query(streaming_query)

        logger.info("Kafka Spark sale processing completed")

        draw_line()
    finally:
        stop_session(session)
        draw_line()


def start_sale_event_stream(session: SparkSession, ingestion_time: datetime) -> StreamingQuery:
    logger.info("Reading sale events from Kafka topic %s", ec.KAFKA_TOPIC)
    kafka_dataframe = kafka_spark_sale_service.read_sale_event_stream(session)

    logger.info("Parsing Kafka sale events")
    sale_event_dataframe = kafka_spark_sale_service.parse_sale_event_stream(kafka_dataframe)

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
        datalake_spark_sale_service.append(dataframe=raw_output_dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME, path=raw_sale_data_path)

        logger.info("Appending cleaned sale data to %s", cleaned_sale_data_path)
        datalake_spark_sale_service.append(dataframe=cleaned_output_dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME, path=cleaned_sale_data_path)

        logger.info("Appending enriched sale data to %s", enriched_sale_data_path)
        datalake_spark_sale_service.append(dataframe=enriched_output_dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME, path=enriched_sale_data_path)

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

    logger.info("Available Kafka sale events were processed")


def show_pipeline_results(ingestion_time: str) -> None:
    session = data_processor_connection_factory.create_connection()
    parsed_ingestion_time = datetime.fromisoformat(ingestion_time)

    try:
        draw_line()

        enriched_sale_data_path = build_sale_datalake_path(layer=DatalakeLayer.ENRICHED, ingestion_time=parsed_ingestion_time)

        logger.info("Reading enriched sale data from %s", enriched_sale_data_path)
        enriched_dataframe = datalake_spark_sale_service.read(session=session, bucket_name=ec.DATALAKE_BUCKET_NAME, path=enriched_sale_data_path)

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
        logger.info("Revenue by category from Datawarehouse:\n%s", revenue_by_category_datawarehouse_dataframe.to_string(index=False))

        logger.info("Calculating revenue by country with Datawarehouse")
        revenue_by_country_datawarehouse_dataframe = datawarehouse_sale_service.get_revenue_by_country()
        logger.info("Revenue by country from Datawarehouse:\n%s", revenue_by_country_datawarehouse_dataframe.to_string(index=False))

        draw_line()
    finally:
        stop_session(session)
        draw_line()


def stop_session(session: SparkSession) -> None:
    logger.info("Stopping Spark session")
    session.stop()


def draw_line() -> None:
    logger.info(100 * "=")


with DAG(
        dag_id=DAG_ID,
        description="Publish CSV sale events to Kafka and process them with Spark Structured Streaming",
        schedule=None,
        start_date=DAG_START_DATE,
        catchup=False,
        max_active_runs=1,
        default_args={
            "owner": "sale-platform",
            "retries": 0,
            "retry_delay": timedelta(minutes=1),
        },
        tags=["sale", "kafka", "spark", "streaming"],
) as dag:
    create_ingestion_time_task = PythonOperator(
        task_id="create_ingestion_time",
        python_callable=create_ingestion_time,
    )

    publish_sale_events_task = PythonOperator(
        task_id="publish_sale_events",
        python_callable=publish_sale_events,
    )

    process_sale_event_stream_task = PythonOperator(
        task_id="process_sale_event_stream",
        python_callable=process_sale_event_stream,
        op_kwargs={"ingestion_time": "{{ ti.xcom_pull(task_ids='create_ingestion_time') }}"},
    )

    show_pipeline_results_task = PythonOperator(
        task_id="show_pipeline_results",
        python_callable=show_pipeline_results,
        op_kwargs={"ingestion_time": "{{ ti.xcom_pull(task_ids='create_ingestion_time') }}"},
    )

    create_ingestion_time_task >> publish_sale_events_task >> process_sale_event_stream_task >> show_pipeline_results_task