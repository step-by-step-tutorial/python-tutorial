import logging
from datetime import UTC, datetime
from typing import Callable, TypeVar

from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG
from pyspark.sql import SparkSession

from app_config import env_config as ec
from app_config.dataframe_schema import SCHEMA
from factory import data_processor_connection_factory
from service import database_sale_service, datalake_sale_service, datawarehouse_sale_service, spark_sale_service
from util.datalake_utils import DatalakeLayer, build_sale_datalake_path

logger = logging.getLogger(__name__)

DAG_ID = "spark_sale_etl_pipeline"

ResultType = TypeVar("ResultType")


def execute_with_spark_session(operation: Callable[[SparkSession], ResultType]) -> ResultType:
    session = data_processor_connection_factory.create_connection()

    try:
        return operation(session)
    finally:
        stop_session(session)


def generate_ingestion_time() -> str:
    ingestion_time = datetime.now(UTC).isoformat()
    logger.info("Generated Spark pipeline ingestion time: %s", ingestion_time)
    return ingestion_time


def upload_raw_sale_data(ingestion_time: str) -> str:
    resolved_ingestion_time = datetime.fromisoformat(ingestion_time)
    raw_sale_data_path = build_sale_datalake_path(layer=DatalakeLayer.RAW, ingestion_time=resolved_ingestion_time)

    def operation(session: SparkSession) -> str:
        logger.info("Reading sale data from %s", ec.DATA_FILE)
        dataframe = spark_sale_service.read_data(session=session, file_name=ec.DATA_FILE, schema=SCHEMA)

        logger.info("Uploading raw sale data to %s", raw_sale_data_path)
        datalake_sale_service.overwrite(dataframe=dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME, path=raw_sale_data_path)

        return raw_sale_data_path

    return execute_with_spark_session(operation)


def clean_sale_data(raw_sale_data_path: str, ingestion_time: str) -> str:
    resolved_ingestion_time = datetime.fromisoformat(ingestion_time)
    cleaned_sale_data_path = build_sale_datalake_path(layer=DatalakeLayer.CLEANED, ingestion_time=resolved_ingestion_time)

    def operation(session: SparkSession) -> str:
        logger.info("Reading raw sale data from %s", raw_sale_data_path)
        dataframe = datalake_sale_service.read(session=session, bucket_name=ec.DATALAKE_BUCKET_NAME, path=raw_sale_data_path)

        logger.info("Cleaning sale data")
        cleaned_dataframe = spark_sale_service.clean_data(dataframe)

        logger.info("Uploading cleaned sale data to %s", cleaned_sale_data_path)
        datalake_sale_service.overwrite(dataframe=cleaned_dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME, path=cleaned_sale_data_path)

        return cleaned_sale_data_path

    return execute_with_spark_session(operation)


def enrich_sale_data(cleaned_sale_data_path: str, ingestion_time: str) -> str:
    resolved_ingestion_time = datetime.fromisoformat(ingestion_time)
    enriched_sale_data_path = build_sale_datalake_path(layer=DatalakeLayer.ENRICHED, ingestion_time=resolved_ingestion_time)

    def operation(session: SparkSession) -> str:
        logger.info("Reading cleaned sale data from %s", cleaned_sale_data_path)
        dataframe = datalake_sale_service.read(session=session, bucket_name=ec.DATALAKE_BUCKET_NAME, path=cleaned_sale_data_path)

        logger.info("Enriching sale data")
        enriched_dataframe = spark_sale_service.enrich_data(dataframe)

        logger.info("Uploading enriched sale data to %s", enriched_sale_data_path)
        datalake_sale_service.overwrite(dataframe=enriched_dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME, path=enriched_sale_data_path)

        return enriched_sale_data_path

    return execute_with_spark_session(operation)


def populate_database(enriched_sale_data_path: str) -> None:
    def operation(session: SparkSession) -> None:
        logger.info("Reading enriched sale data from %s", enriched_sale_data_path)
        enriched_dataframe = datalake_sale_service.read(session=session, bucket_name=ec.DATALAKE_BUCKET_NAME, path=enriched_sale_data_path)

        logger.info("Populating database")
        database_sale_service.populate(enriched_dataframe)

    execute_with_spark_session(operation)


def populate_datawarehouse(enriched_sale_data_path: str) -> None:
    def operation(session: SparkSession) -> None:
        logger.info("Reading enriched sale data from %s", enriched_sale_data_path)
        enriched_dataframe = datalake_sale_service.read(session=session, bucket_name=ec.DATALAKE_BUCKET_NAME, path=enriched_sale_data_path)

        logger.info("Populating data warehouse")
        datawarehouse_sale_service.populate(enriched_dataframe.toPandas())

    execute_with_spark_session(operation)


def show_enriched_sale_data(enriched_sale_data_path: str) -> None:
    def operation(session: SparkSession) -> None:
        logger.info("Reading enriched sale data from %s", enriched_sale_data_path)
        enriched_dataframe = datalake_sale_service.read(session=session, bucket_name=ec.DATALAKE_BUCKET_NAME, path=enriched_sale_data_path)

        logger.info("Showing enriched sale data")
        enriched_dataframe.show(10, truncate=False)

    execute_with_spark_session(operation)


def calculate_revenue_by_category_with_spark(enriched_sale_data_path: str) -> None:
    def operation(session: SparkSession) -> None:
        logger.info("Reading enriched sale data from %s", enriched_sale_data_path)
        enriched_dataframe = datalake_sale_service.read(session=session, bucket_name=ec.DATALAKE_BUCKET_NAME, path=enriched_sale_data_path)

        logger.info("Calculating revenue by category with Spark")
        revenue_by_category_dataframe = spark_sale_service.get_revenue_by_category(enriched_dataframe)
        revenue_by_category_dataframe.show(truncate=False)

    execute_with_spark_session(operation)


def calculate_revenue_by_country_with_spark(enriched_sale_data_path: str) -> None:
    def operation(session: SparkSession) -> None:
        logger.info("Reading enriched sale data from %s", enriched_sale_data_path)
        enriched_dataframe = datalake_sale_service.read(session=session, bucket_name=ec.DATALAKE_BUCKET_NAME, path=enriched_sale_data_path)

        logger.info("Calculating revenue by country with Spark")
        revenue_by_country_dataframe = spark_sale_service.get_revenue_by_country(enriched_dataframe)
        revenue_by_country_dataframe.show(truncate=False)

    execute_with_spark_session(operation)


def calculate_revenue_by_category_with_datawarehouse() -> None:
    logger.info("Calculating revenue by category from data warehouse")
    revenue_by_category_dataframe = datawarehouse_sale_service.get_revenue_by_category()
    logger.info("Data warehouse revenue by category:\n%s", revenue_by_category_dataframe.to_string(index=False))


def calculate_revenue_by_country_with_datawarehouse() -> None:
    logger.info("Calculating revenue by country from data warehouse")
    revenue_by_country_dataframe = datawarehouse_sale_service.get_revenue_by_country()
    logger.info("Data warehouse revenue by country:\n%s", revenue_by_country_dataframe.to_string(index=False))


def stop_session(session: SparkSession) -> None:
    logger.info("Stopping Spark session")
    session.stop()


with DAG(
        dag_id=DAG_ID,
        start_date=datetime(2026, 1, 1, tzinfo=UTC),
        schedule=None,
        catchup=False,
        tags=["sale", "etl", "spark", "datalake"],
) as dag:
    generate_ingestion_time_operation = PythonOperator(
        task_id="generate_ingestion_time",
        python_callable=generate_ingestion_time,
    )

    upload_raw_sale_data_operation = PythonOperator(
        task_id="upload_raw_sale_data",
        python_callable=upload_raw_sale_data,
        op_kwargs={
            "ingestion_time": generate_ingestion_time_operation.output,
        },
    )

    clean_sale_data_operation = PythonOperator(
        task_id="clean_sale_data",
        python_callable=clean_sale_data,
        op_kwargs={
            "raw_sale_data_path": upload_raw_sale_data_operation.output,
            "ingestion_time": generate_ingestion_time_operation.output,
        },
    )

    enrich_sale_data_operation = PythonOperator(
        task_id="enrich_sale_data",
        python_callable=enrich_sale_data,
        op_kwargs={
            "cleaned_sale_data_path": clean_sale_data_operation.output,
            "ingestion_time": generate_ingestion_time_operation.output,
        },
    )

    populate_database_operation = PythonOperator(
        task_id="populate_database",
        python_callable=populate_database,
        op_kwargs={
            "enriched_sale_data_path": enrich_sale_data_operation.output,
        },
    )

    populate_datawarehouse_operation = PythonOperator(
        task_id="populate_datawarehouse",
        python_callable=populate_datawarehouse,
        op_kwargs={
            "enriched_sale_data_path": enrich_sale_data_operation.output,
        },
    )

    show_enriched_sale_data_operation = PythonOperator(
        task_id="show_enriched_sale_data",
        python_callable=show_enriched_sale_data,
        op_kwargs={
            "enriched_sale_data_path": enrich_sale_data_operation.output,
        },
    )

    calculate_revenue_by_category_with_spark_operation = PythonOperator(
        task_id="calculate_revenue_by_category_with_spark",
        python_callable=calculate_revenue_by_category_with_spark,
        op_kwargs={
            "enriched_sale_data_path": enrich_sale_data_operation.output,
        },
    )

    calculate_revenue_by_country_with_spark_operation = PythonOperator(
        task_id="calculate_revenue_by_country_with_spark",
        python_callable=calculate_revenue_by_country_with_spark,
        op_kwargs={
            "enriched_sale_data_path": enrich_sale_data_operation.output,
        },
    )

    calculate_revenue_by_category_with_datawarehouse_operation = PythonOperator(
        task_id="calculate_revenue_by_category_with_datawarehouse",
        python_callable=calculate_revenue_by_category_with_datawarehouse,
    )

    calculate_revenue_by_country_with_datawarehouse_operation = PythonOperator(
        task_id="calculate_revenue_by_country_with_datawarehouse",
        python_callable=calculate_revenue_by_country_with_datawarehouse,
    )

    generate_ingestion_time_operation >> upload_raw_sale_data_operation >> clean_sale_data_operation >> enrich_sale_data_operation

    enrich_sale_data_operation >> [
        populate_database_operation,
        populate_datawarehouse_operation,
        show_enriched_sale_data_operation,
        calculate_revenue_by_category_with_spark_operation,
        calculate_revenue_by_country_with_spark_operation,
    ]

    populate_datawarehouse_operation >> [
        calculate_revenue_by_category_with_datawarehouse_operation,
        calculate_revenue_by_country_with_datawarehouse_operation,
    ]