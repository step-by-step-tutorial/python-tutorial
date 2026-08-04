import logging
from datetime import datetime
from uuid import uuid4

from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG

from app_config import env_config as ec
from service import csv_sale_service, database_sale_service, datalake_sale_service, datawarehouse_sale_service

logger = logging.getLogger(__name__)

DAG_ID = "sale_etl_pipeline"


def generate_run_id() -> str:
    run_id = str(uuid4())
    logger.info("Generated pipeline run ID: %s", run_id)
    return run_id


def upload_raw_sale_data(run_id: str) -> str:
    logger.info("Reading sale data from %s", ec.DATA_FILE)
    dataframe = csv_sale_service.read_data(file_name=ec.DATA_FILE)

    logger.info("Uploading raw sale data to the data lake")
    return datalake_sale_service.upload_as_parquet(dataframe=dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME,
                                                   object_key=ec.DATALAKE_RAW_SALE_DATA, run_id=run_id)


def clean_sale_data(raw_parquet_key: str, run_id: str) -> str:
    logger.info("Reading raw sale data from %s", raw_parquet_key)
    dataframe = datalake_sale_service.read_parquet(bucket_name=ec.DATALAKE_BUCKET_NAME, object_key=raw_parquet_key)

    logger.info("Cleaning sale data")
    cleaned_dataframe = csv_sale_service.clean_data(dataframe)

    logger.info("Uploading cleaned sale data to the data lake")
    return datalake_sale_service.upload_as_parquet(dataframe=cleaned_dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME,
                                                   object_key=ec.DATALAKE_CLEANED_SALE_DATA, run_id=run_id)


def enrich_sale_data(cleaned_parquet_key: str, run_id: str) -> str:
    logger.info("Reading cleaned sale data from %s", cleaned_parquet_key)
    dataframe = datalake_sale_service.read_parquet(bucket_name=ec.DATALAKE_BUCKET_NAME, object_key=cleaned_parquet_key)

    logger.info("Enriching sale data")
    enriched_dataframe = csv_sale_service.enrich_data(dataframe)

    logger.info("Uploading enriched sale data to the data lake")
    return datalake_sale_service.upload_as_parquet(dataframe=enriched_dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME,
                                                   object_key=ec.DATALAKE_ENRICHED_SALE_DATA, run_id=run_id)


def populate_database(enriched_parquet_key: str) -> None:
    logger.info("Reading enriched sale data from %s", enriched_parquet_key)
    enriched_dataframe = datalake_sale_service.read_parquet(bucket_name=ec.DATALAKE_BUCKET_NAME,
                                                            object_key=enriched_parquet_key)

    logger.info("Populating database")
    database_sale_service.populate(enriched_dataframe)


def populate_datawarehouse(enriched_parquet_key: str) -> None:
    logger.info("Reading enriched sale data from %s", enriched_parquet_key)
    enriched_dataframe = datalake_sale_service.read_parquet(bucket_name=ec.DATALAKE_BUCKET_NAME,
                                                            object_key=enriched_parquet_key)

    logger.info("Populating data warehouse")
    datawarehouse_sale_service.populate(enriched_dataframe)


def calculate_revenue_by_category(enriched_parquet_key: str) -> None:
    logger.info("Reading enriched sale data from %s", enriched_parquet_key)
    enriched_dataframe = datalake_sale_service.read_parquet(bucket_name=ec.DATALAKE_BUCKET_NAME,
                                                            object_key=enriched_parquet_key)

    logger.info("Calculating revenue by category")
    revenue_by_category_dataframe = csv_sale_service.get_revenue_by_category(enriched_dataframe)
    logger.info("Revenue by category:\n%s", revenue_by_category_dataframe.to_string(index=False))


def calculate_revenue_by_country(enriched_parquet_key: str) -> None:
    logger.info("Reading enriched sale data from %s", enriched_parquet_key)
    enriched_dataframe = datalake_sale_service.read_parquet(bucket_name=ec.DATALAKE_BUCKET_NAME,
                                                            object_key=enriched_parquet_key)

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
        start_date=datetime(2026, 1, 1),
        schedule=None,
        catchup=False,
        tags=["sale", "etl", "datalake"],
) as dag:
    generate_run_id_operation = PythonOperator(
        task_id="generate_run_id",
        python_callable=generate_run_id,
    )

    upload_raw_sale_data_operation = PythonOperator(
        task_id="upload_raw_sale_data",
        python_callable=upload_raw_sale_data,
        op_kwargs={
            "run_id": generate_run_id_operation.output,
        },
    )

    clean_sale_data_operation = PythonOperator(
        task_id="clean_sale_data",
        python_callable=clean_sale_data,
        op_kwargs={
            "raw_parquet_key": upload_raw_sale_data_operation.output,
            "run_id": generate_run_id_operation.output,
        },
    )

    enrich_sale_data_operation = PythonOperator(
        task_id="enrich_sale_data",
        python_callable=enrich_sale_data,
        op_kwargs={
            "cleaned_parquet_key": clean_sale_data_operation.output,
            "run_id": generate_run_id_operation.output,
        },
    )

    populate_database_operation = PythonOperator(
        task_id="populate_database",
        python_callable=populate_database,
        op_kwargs={
            "enriched_parquet_key": enrich_sale_data_operation.output,
        },
    )

    populate_datawarehouse_operation = PythonOperator(
        task_id="populate_datawarehouse",
        python_callable=populate_datawarehouse,
        op_kwargs={
            "enriched_parquet_key": enrich_sale_data_operation.output,
        },
    )

    calculate_revenue_by_category_operation = PythonOperator(
        task_id="calculate_revenue_by_category",
        python_callable=calculate_revenue_by_category,
        op_kwargs={
            "enriched_parquet_key": enrich_sale_data_operation.output,
        },
    )

    calculate_revenue_by_country_operation = PythonOperator(
        task_id="calculate_revenue_by_country",
        python_callable=calculate_revenue_by_country,
        op_kwargs={
            "enriched_parquet_key": enrich_sale_data_operation.output,
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

    generate_run_id_operation >> upload_raw_sale_data_operation >> clean_sale_data_operation >> enrich_sale_data_operation

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
