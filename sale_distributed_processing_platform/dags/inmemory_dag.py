import logging
from datetime import UTC, datetime

from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG

from app_config import env_config as ec
from service import csv_sale_service
from service.database import database_sale_service
from service.datalake import datalake_pandas_sale_service
from service.datawarehouse import datawarehouse_sale_service
from util.datalake_utils import DatalakeLayer, build_datalake_path

logger = logging.getLogger(__name__)

DAG_ID = "inmemory_etl_dag"


def generate_ingestion_time() -> str:
    ingestion_time = datetime.now(UTC).isoformat()
    logger.info("Generated pipeline ingestion time: %s", ingestion_time)
    return ingestion_time


def upload_raw_sale_data(ingestion_time: str) -> str:
    resolved_ingestion_time = datetime.fromisoformat(ingestion_time)
    raw_sale_data_path = build_datalake_path(layer=DatalakeLayer.RAW, ingestion_time=resolved_ingestion_time)

    logger.info("Reading sale data from %s", ec.DATA_FILE)
    dataframe = csv_sale_service.read_data(file_name=ec.DATA_FILE)

    logger.info("Uploading raw sale data to %s", raw_sale_data_path)
    datalake_pandas_sale_service.upload_parquet(dataframe=dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME,
                                                path=raw_sale_data_path)

    return raw_sale_data_path


def clean_sale_data(raw_sale_data_path: str, ingestion_time: str) -> str:
    resolved_ingestion_time = datetime.fromisoformat(ingestion_time)
    cleaned_sale_data_path = build_datalake_path(layer=DatalakeLayer.CLEANED,
                                                 ingestion_time=resolved_ingestion_time)

    logger.info("Reading raw sale data from %s", raw_sale_data_path)
    dataframe = datalake_pandas_sale_service.download_parquet(bucket_name=ec.DATALAKE_BUCKET_NAME,
                                                              path=raw_sale_data_path)

    logger.info("Cleaning sale data")
    cleaned_dataframe = csv_sale_service.clean_data(dataframe)

    logger.info("Uploading cleaned sale data to %s", cleaned_sale_data_path)
    datalake_pandas_sale_service.upload_parquet(dataframe=cleaned_dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME,
                                                path=cleaned_sale_data_path)

    return cleaned_sale_data_path


def enrich_sale_data(cleaned_sale_data_path: str, ingestion_time: str) -> str:
    resolved_ingestion_time = datetime.fromisoformat(ingestion_time)
    enriched_sale_data_path = build_datalake_path(layer=DatalakeLayer.ENRICHED,
                                                  ingestion_time=resolved_ingestion_time)

    logger.info("Reading cleaned sale data from %s", cleaned_sale_data_path)
    dataframe = datalake_pandas_sale_service.download_parquet(bucket_name=ec.DATALAKE_BUCKET_NAME,
                                                              path=cleaned_sale_data_path)

    logger.info("Enriching sale data")
    enriched_dataframe = csv_sale_service.enrich_data(dataframe)

    logger.info("Uploading enriched sale data to %s", enriched_sale_data_path)
    datalake_pandas_sale_service.upload_parquet(dataframe=enriched_dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME,
                                                path=enriched_sale_data_path)

    return enriched_sale_data_path


def populate_database(enriched_sale_data_path: str) -> None:
    logger.info("Reading enriched sale data from %s", enriched_sale_data_path)
    enriched_dataframe = datalake_pandas_sale_service.download_parquet(bucket_name=ec.DATALAKE_BUCKET_NAME,
                                                                       path=enriched_sale_data_path)

    logger.info("Populating database")
    database_sale_service.populate(enriched_dataframe)


def populate_datawarehouse(enriched_sale_data_path: str) -> None:
    logger.info("Reading enriched sale data from %s", enriched_sale_data_path)
    enriched_dataframe = datalake_pandas_sale_service.download_parquet(bucket_name=ec.DATALAKE_BUCKET_NAME,
                                                                       path=enriched_sale_data_path)

    logger.info("Populating data warehouse")
    datawarehouse_sale_service.populate(enriched_dataframe)


def calculate_revenue_by_category(enriched_sale_data_path: str) -> None:
    logger.info("Reading enriched sale data from %s", enriched_sale_data_path)
    enriched_dataframe = datalake_pandas_sale_service.download_parquet(bucket_name=ec.DATALAKE_BUCKET_NAME,
                                                                       path=enriched_sale_data_path)

    logger.info("Calculating revenue by category")
    revenue_by_category_dataframe = csv_sale_service.get_revenue_by_category(enriched_dataframe)
    logger.info("Revenue by category:\n%s", revenue_by_category_dataframe.to_string(index=False))


def calculate_revenue_by_country(enriched_sale_data_path: str) -> None:
    logger.info("Reading enriched sale data from %s", enriched_sale_data_path)
    enriched_dataframe = datalake_pandas_sale_service.download_parquet(bucket_name=ec.DATALAKE_BUCKET_NAME,
                                                                       path=enriched_sale_data_path)

    logger.info("Calculating revenue by country")
    revenue_by_country_dataframe = csv_sale_service.get_revenue_by_country(enriched_dataframe)
    logger.info("Revenue by country:\n%s", revenue_by_country_dataframe.to_string(index=False))


def calculate_datawarehouse_revenue_by_category() -> None:
    logger.info("Calculating revenue by category from data warehouse")
    revenue_by_category_dataframe = datawarehouse_sale_service.get_revenue_by_category()
    logger.info("Data warehouse revenue by category:\n%s", revenue_by_category_dataframe.to_string(index=False))


def calculate_datawarehouse_revenue_by_country() -> None:
    logger.info("Calculating revenue by country from data warehouse")
    revenue_by_country_dataframe = datawarehouse_sale_service.get_revenue_by_country()
    logger.info("Data warehouse revenue by country:\n%s", revenue_by_country_dataframe.to_string(index=False))


with DAG(
        dag_id=DAG_ID,
        start_date=datetime(2026, 1, 1, tzinfo=UTC),
        schedule=None,
        catchup=False,
        tags=["sale", "etl", "datalake"],
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

    calculate_revenue_by_category_operation = PythonOperator(
        task_id="calculate_revenue_by_category",
        python_callable=calculate_revenue_by_category,
        op_kwargs={
            "enriched_sale_data_path": enrich_sale_data_operation.output,
        },
    )

    calculate_revenue_by_country_operation = PythonOperator(
        task_id="calculate_revenue_by_country",
        python_callable=calculate_revenue_by_country,
        op_kwargs={
            "enriched_sale_data_path": enrich_sale_data_operation.output,
        },
    )

    calculate_datawarehouse_revenue_by_category_operation = PythonOperator(
        task_id="calculate_datawarehouse_revenue_by_category",
        python_callable=calculate_datawarehouse_revenue_by_category,
    )

    calculate_datawarehouse_revenue_by_country_operation = PythonOperator(
        task_id="calculate_datawarehouse_revenue_by_country",
        python_callable=calculate_datawarehouse_revenue_by_country,
    )

    generate_ingestion_time_operation >> upload_raw_sale_data_operation >> clean_sale_data_operation >> enrich_sale_data_operation

    enrich_sale_data_operation >> [
        populate_database_operation,
        populate_datawarehouse_operation,
        calculate_revenue_by_category_operation,
        calculate_revenue_by_country_operation,
    ]

    populate_datawarehouse_operation >> [
        calculate_datawarehouse_revenue_by_category_operation,
        calculate_datawarehouse_revenue_by_country_operation,
    ]
