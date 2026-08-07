import logging
from datetime import UTC, datetime
from typing import Callable, TypeVar

from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG
from pyspark.sql import SparkSession

from app_config import env_config as ec
from app_config.dataframe_schema import SCHEMA
from factory import data_processor_connection_factory
from service import spark_sale_service
from service.database import database_sale_service
from service.datalake import datalake_spark_sale_service
from service.datawarehouse import datawarehouse_sale_service
from util.datalake_utils import DatalakeLayer, build_datalake_path

logger = logging.getLogger(__name__)

DAG_ID = "spark__etl_dag"

ResultType = TypeVar("ResultType")


def execute_with_spark_session(operation: Callable[[SparkSession], ResultType]) -> ResultType:
    session = data_processor_connection_factory.create_connection()

    try:
        return operation(session)
    finally:
        logger.info("Stopping Spark session")
        session.stop()


def generate_ingestion_time() -> str:
    ingestion_time = datetime.now(UTC).isoformat()
    logger.info("Generated ingestion time %s", ingestion_time)
    return ingestion_time


def store_raw_data(ingestion_time: str) -> str:
    resolved_ingestion_time = datetime.fromisoformat(ingestion_time)
    raw_data_path = build_datalake_path(DatalakeLayer.RAW, resolved_ingestion_time)

    def operation(session: SparkSession) -> str:
        logger.info("Reading data from file %s", ec.DATA_FILE)
        dataframe = spark_sale_service.read_data(session=session, file_name=ec.DATA_FILE, schema=SCHEMA)

        logger.info("Storing raw data in datalake path %s", raw_data_path)
        datalake_spark_sale_service.overwrite(dataframe=dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME, path=raw_data_path)

        return raw_data_path

    return execute_with_spark_session(operation)


def clean_data(raw_data_path: str, ingestion_time: str) -> str:
    resolved_ingestion_time = datetime.fromisoformat(ingestion_time)
    cleaned_data_path = build_datalake_path(DatalakeLayer.CLEANED, resolved_ingestion_time)

    def operation(session: SparkSession) -> str:
        logger.info("Reading raw data from datalake path %s", raw_data_path)
        dataframe = datalake_spark_sale_service.read(session=session, bucket_name=ec.DATALAKE_BUCKET_NAME, path=raw_data_path)

        logger.info("Cleaning data")
        cleaned_dataframe = spark_sale_service.clean_data(dataframe)

        logger.info("Storing cleaned data in datalake path %s", cleaned_data_path)
        datalake_spark_sale_service.overwrite(dataframe=cleaned_dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME, path=cleaned_data_path)

        return cleaned_data_path

    return execute_with_spark_session(operation)


def enrich_data(cleaned_data_path: str, ingestion_time: str) -> str:
    resolved_ingestion_time = datetime.fromisoformat(ingestion_time)
    enriched_data_path = build_datalake_path(DatalakeLayer.ENRICHED, resolved_ingestion_time)

    def operation(session: SparkSession) -> str:
        logger.info("Reading cleaned data from datalake path %s", cleaned_data_path)
        dataframe = datalake_spark_sale_service.read(session=session, bucket_name=ec.DATALAKE_BUCKET_NAME, path=cleaned_data_path)

        logger.info("Enriching data")
        enriched_dataframe = spark_sale_service.enrich_data(dataframe)

        logger.info("Storing enriched data in datalake path %s", enriched_data_path)
        datalake_spark_sale_service.overwrite(dataframe=enriched_dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME, path=enriched_data_path)

        return enriched_data_path

    return execute_with_spark_session(operation)


def populate_database(enriched_data_path: str) -> None:
    def operation(session: SparkSession) -> None:
        logger.info("Reading enriched data from datalake path %s", enriched_data_path)
        dataframe = datalake_spark_sale_service.read(session=session, bucket_name=ec.DATALAKE_BUCKET_NAME, path=enriched_data_path)

        logger.info("Populating operational database with enriched data")
        database_sale_service.populate(dataframe)

    execute_with_spark_session(operation)


def populate_datawarehouse(enriched_data_path: str) -> None:
    def operation(session: SparkSession) -> None:
        logger.info("Reading enriched data from datalake path %s", enriched_data_path)
        dataframe = datalake_spark_sale_service.read(session=session, bucket_name=ec.DATALAKE_BUCKET_NAME, path=enriched_data_path)

        logger.info("Populating data warehouse with enriched data")
        datawarehouse_sale_service.populate(dataframe.toPandas())

    execute_with_spark_session(operation)


def show_enriched_data(enriched_data_path: str) -> None:
    def operation(session: SparkSession) -> None:
        logger.info("Reading enriched data from datalake path %s", enriched_data_path)
        dataframe = datalake_spark_sale_service.read(session=session, bucket_name=ec.DATALAKE_BUCKET_NAME, path=enriched_data_path)

        logger.info("Displaying enriched data")
        dataframe.show(10, truncate=False)

    execute_with_spark_session(operation)


def show_revenue_by_category(enriched_data_path: str) -> None:
    def operation(session: SparkSession) -> None:
        logger.info("Reading enriched data from datalake path %s", enriched_data_path)
        dataframe = datalake_spark_sale_service.read(session=session, bucket_name=ec.DATALAKE_BUCKET_NAME, path=enriched_data_path)

        logger.info("Calculating revenue by category using Spark")
        revenue_by_category = spark_sale_service.get_revenue_by_category(dataframe)
        revenue_by_category.show(truncate=False)

    execute_with_spark_session(operation)


def show_revenue_by_country(enriched_data_path: str) -> None:
    def operation(session: SparkSession) -> None:
        logger.info("Reading enriched data from datalake path %s", enriched_data_path)
        dataframe = datalake_spark_sale_service.read(session=session, bucket_name=ec.DATALAKE_BUCKET_NAME, path=enriched_data_path)

        logger.info("Calculating revenue by country using Spark")
        revenue_by_country = spark_sale_service.get_revenue_by_country(dataframe)
        revenue_by_country.show(truncate=False)

    execute_with_spark_session(operation)


def show_datawarehouse_revenue_by_category() -> None:
    logger.info("Calculating revenue by category using the data warehouse")
    revenue_by_category = datawarehouse_sale_service.get_revenue_by_category()
    logger.info("Data warehouse revenue by category:\n%s", revenue_by_category.to_string(index=False))


def show_datawarehouse_revenue_by_country() -> None:
    logger.info("Calculating revenue by country using the data warehouse")
    revenue_by_country = datawarehouse_sale_service.get_revenue_by_country()
    logger.info("Data warehouse revenue by country:\n%s", revenue_by_country.to_string(index=False))


with DAG(
        dag_id=DAG_ID,
        start_date=datetime(2026, 1, 1, tzinfo=UTC),
        schedule=None,
        catchup=False,
        tags={"spark", "etl", "datalake"},
) as dag:

    generate_ingestion_time_task = PythonOperator(
        task_id="generate_ingestion_time",
        python_callable=generate_ingestion_time,
    )

    store_raw_data_task = PythonOperator(
        task_id="store_raw_data",
        python_callable=store_raw_data,
        op_kwargs={"ingestion_time": generate_ingestion_time_task.output},
    )

    clean_data_task = PythonOperator(
        task_id="clean_data",
        python_callable=clean_data,
        op_kwargs={
            "raw_data_path": store_raw_data_task.output,
            "ingestion_time": generate_ingestion_time_task.output,
        },
    )

    enrich_data_task = PythonOperator(
        task_id="enrich_data",
        python_callable=enrich_data,
        op_kwargs={
            "cleaned_data_path": clean_data_task.output,
            "ingestion_time": generate_ingestion_time_task.output,
        },
    )

    populate_database_task = PythonOperator(
        task_id="populate_database",
        python_callable=populate_database,
        op_kwargs={"enriched_data_path": enrich_data_task.output},
    )

    populate_datawarehouse_task = PythonOperator(
        task_id="populate_datawarehouse",
        python_callable=populate_datawarehouse,
        op_kwargs={"enriched_data_path": enrich_data_task.output},
    )

    show_enriched_data_task = PythonOperator(
        task_id="show_enriched_data",
        python_callable=show_enriched_data,
        op_kwargs={"enriched_data_path": enrich_data_task.output},
    )

    show_revenue_by_category_task = PythonOperator(
        task_id="show_revenue_by_category",
        python_callable=show_revenue_by_category,
        op_kwargs={"enriched_data_path": enrich_data_task.output},
    )

    show_revenue_by_country_task = PythonOperator(
        task_id="show_revenue_by_country",
        python_callable=show_revenue_by_country,
        op_kwargs={"enriched_data_path": enrich_data_task.output},
    )

    show_datawarehouse_revenue_by_category_task = PythonOperator(
        task_id="show_datawarehouse_revenue_by_category",
        python_callable=show_datawarehouse_revenue_by_category,
    )

    show_datawarehouse_revenue_by_country_task = PythonOperator(
        task_id="show_datawarehouse_revenue_by_country",
        python_callable=show_datawarehouse_revenue_by_country,
    )

    generate_ingestion_time_task >> store_raw_data_task >> clean_data_task >> enrich_data_task

    enrich_data_task >> [
        populate_database_task,
        populate_datawarehouse_task,
        show_enriched_data_task,
        show_revenue_by_category_task,
        show_revenue_by_country_task,
    ]

    populate_datawarehouse_task >> [
        show_datawarehouse_revenue_by_category_task,
        show_datawarehouse_revenue_by_country_task,
    ]