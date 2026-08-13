import logging
from datetime import UTC, datetime, timedelta

import pendulum
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.streaming import StreamingQuery

from app_config import env_config as ec
from app_config.dataframe_schema import SCHEMA
from factory import spark_connection_factory
from service import spark_sale_service, spark_streaming_service
from service.database import database_sale_service
from service.datalake import distributed_datalake_service
from service.datawarehouse import datawarehouse_sale_service
from streaming import csv_publisher
from util.datalake_utils import DatalakeLayer, generate_relative_path, persisted_dataframes
from util.log_utils import log_line

logger = logging.getLogger(__name__)

DAG_ID = "spark_based_streaming_dag"
DAG_START_DATE = pendulum.datetime(2026, 1, 1, tz="UTC")


def generate_ingestion_time() -> str:
    ingestion_time = datetime.now(UTC).isoformat()
    logger.info("Generated ingestion time %s", ingestion_time)
    return ingestion_time


def publish_events() -> None:
    logger.info("Publishing events from file %s to streaming topic %s", ec.DATA_FILE, ec.STREAMING_TOPIC)
    published_event_count = csv_publisher.publish(ec.DATA_FILE)
    logger.info("Published %s events to streaming topic %s", published_event_count, ec.STREAMING_TOPIC)


def process_stream(ingestion_time: str) -> None:
    session = spark_connection_factory.create_connection()
    resolved_ingestion_time = datetime.fromisoformat(ingestion_time)

    try:
        log_line()
        logger.info("Starting Spark streaming pipeline with ingestion time %s", resolved_ingestion_time)

        streaming_query = start_stream(session, resolved_ingestion_time)
        streaming_query.awaitTermination()

        logger.info("Spark streaming pipeline completed successfully")
    finally:
        logger.info("Stopping Spark session")
        session.stop()
        log_line()


def start_stream(session: SparkSession, ingestion_time: datetime) -> StreamingQuery:
    logger.info("Creating Spark stream for streaming topic %s", ec.STREAMING_TOPIC)

    dataframe = spark_streaming_service.read_stream(session)
    event_dataframe = spark_streaming_service.convert(dataframe, SCHEMA)

    logger.info("Starting streaming query with checkpoint location %s", ec.STREAMING_CHECKPOINT_PATH)

    return (
        event_dataframe.writeStream
        .foreachBatch(lambda dataframe, batch_id: store_batch(dataframe, batch_id, ingestion_time))
        .option("checkpointLocation", ec.STREAMING_CHECKPOINT_PATH)
        .trigger(availableNow=True)
        .start()
    )


def store_batch(dataframe: DataFrame, batch_id: int, ingestion_time: datetime) -> None:
    if dataframe.isEmpty():
        logger.info("Skipping empty Spark micro-batch %s", batch_id)
        return

    logger.info("Processing Spark micro-batch %s", batch_id)

    with persisted_dataframes() as persisted:
        raw_dataframe = spark_streaming_service.append_raw_data(dataframe, ingestion_time).persist()
        persisted.append(raw_dataframe)

        cleaned_dataframe = spark_streaming_service.append_cleaned_data(raw_dataframe, ingestion_time).persist()
        persisted.append(cleaned_dataframe)

        enriched_dataframe = spark_streaming_service.append_enriched_data(cleaned_dataframe, ingestion_time).persist()
        persisted.append(enriched_dataframe)

    logger.info("Completed Spark micro-batch %s", batch_id)


def populate_database(ingestion_time: str) -> None:
    session = spark_connection_factory.create_connection()

    try:
        dataframe = read_enriched_data(session, ingestion_time)

        logger.info("Populating operational database with enriched data")
        database_sale_service.populate(dataframe)
    finally:
        logger.info("Stopping Spark session")
        session.stop()


def populate_datawarehouse(ingestion_time: str) -> None:
    session = spark_connection_factory.create_connection()

    try:
        dataframe = read_enriched_data(session, ingestion_time)

        logger.info("Populating data warehouse with enriched data")
        datawarehouse_sale_service.populate(dataframe.toPandas())
    finally:
        logger.info("Stopping Spark session")
        session.stop()


def show_pipeline_results(ingestion_time: str) -> None:
    session = spark_connection_factory.create_connection()

    try:
        log_line()

        dataframe = read_enriched_data(session, ingestion_time)

        logger.info("Displaying enriched data sample")
        dataframe.show(10)

        logger.info("Calculating revenue by category using Spark")
        revenue_by_category = spark_sale_service.get_revenue_by_category(dataframe)
        revenue_by_category.show()

        logger.info("Calculating revenue by country using Spark")
        revenue_by_country = spark_sale_service.get_revenue_by_country(dataframe)
        revenue_by_country.show()

        logger.info("Calculating revenue by category using the data warehouse")
        datawarehouse_revenue_by_category = datawarehouse_sale_service.get_revenue_by_category()
        logger.info("Data warehouse revenue by category:\n%s", datawarehouse_revenue_by_category.to_string(index=False))

        logger.info("Calculating revenue by country using the data warehouse")
        datawarehouse_revenue_by_country = datawarehouse_sale_service.get_revenue_by_country()
        logger.info("Data warehouse revenue by country:\n%s", datawarehouse_revenue_by_country.to_string(index=False))

    finally:
        logger.info("Stopping Spark session")
        session.stop()
        log_line()


def read_enriched_data(session: SparkSession, ingestion_time: str) -> DataFrame:
    resolved_ingestion_time = datetime.fromisoformat(ingestion_time)
    enriched_data_path = generate_relative_path(DatalakeLayer.ENRICHED, resolved_ingestion_time)

    logger.info("Reading enriched data from datalake path %s", enriched_data_path)

    return distributed_datalake_service.read(
        session=session,
        bucket_name=ec.DATALAKE_BUCKET_NAME,
        path=enriched_data_path,
    )


with DAG(
        dag_id=DAG_ID,
        description="Publish events to streaming and process them with Spark Structured Streaming",
        schedule=None,
        start_date=DAG_START_DATE,
        catchup=False,
        max_active_runs=1,
        default_args={
            "owner": "data-platform",
            "retries": 0,
            "retry_delay": timedelta(minutes=1),
        },
        tags={"streaming", "spark", "datalake"},
) as dag:
    generate_ingestion_time_task = PythonOperator(
        task_id="generate_ingestion_time",
        python_callable=generate_ingestion_time,
    )

    publish_events_task = PythonOperator(
        task_id="publish_events",
        python_callable=publish_events,
    )

    process_stream_task = PythonOperator(
        task_id="process_stream",
        python_callable=process_stream,
        op_kwargs={"ingestion_time": generate_ingestion_time_task.output},
    )

    populate_database_task = PythonOperator(
        task_id="populate_database",
        python_callable=populate_database,
        op_kwargs={"ingestion_time": generate_ingestion_time_task.output},
    )

    populate_datawarehouse_task = PythonOperator(
        task_id="populate_datawarehouse",
        python_callable=populate_datawarehouse,
        op_kwargs={"ingestion_time": generate_ingestion_time_task.output},
    )

    show_pipeline_results_task = PythonOperator(
        task_id="show_pipeline_results",
        python_callable=show_pipeline_results,
        op_kwargs={"ingestion_time": generate_ingestion_time_task.output},
    )

    generate_ingestion_time_task >> publish_events_task >> process_stream_task

    process_stream_task >> [
        populate_database_task,
        populate_datawarehouse_task,
    ]

    [
        populate_database_task,
        populate_datawarehouse_task,
    ] >> show_pipeline_results_task
