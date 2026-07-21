import logging

from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG

import config
from clean_sale_data_util import clean_sale_data
from service.sale_datalake_service import SaleDataLakeService
from file_utils import read_csv
from database_service import DatabaseService
from sale_fact_service import SaleFactService
from transform_sale_data_util import transform_sale_data
from transform_sale_fact_util import transform_sale_fact

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def read_sale_data() -> None:
    sale_dataframe = read_csv(config.RAW_SALE_DATA_FILE_PATH)
    logger.info("Loading sale data from %s (%s rows)", config.RAW_SALE_DATA_FILE_PATH, len(sale_dataframe), )

    datalake_service = SaleDataLakeService()
    datalake_service.upload_as_parquet(
        dataframe=sale_dataframe,
        bucket_name=config.DATALAKE_BUCKET_NAME,
        object_key=config.RAW_SALE_DATA_DATALAKE_PATH,
    )


def clean_sale_data_task() -> None:
    datalake_service = SaleDataLakeService()

    sale_dataframe = datalake_service.read_parquet(
        bucket_name=config.DATALAKE_BUCKET_NAME,
        object_key=config.RAW_SALE_DATA_DATALAKE_PATH,
    )
    logger.info("Cleaning sale data (%s rows)", len(sale_dataframe))

    cleaned_sale_dataframe = clean_sale_data(sale_dataframe)

    datalake_service.upload_as_parquet(
        dataframe=cleaned_sale_dataframe,
        bucket_name=config.DATALAKE_BUCKET_NAME,
        object_key=config.CLEANED_SALE_DATA_DATALAKE_PATH,
    )


def transform_sale_data_task() -> None:
    datalake_service = SaleDataLakeService()
    cleaned_sale_dataframe = datalake_service.read_parquet(
        bucket_name=config.DATALAKE_BUCKET_NAME,
        object_key=config.CLEANED_SALE_DATA_DATALAKE_PATH,
    )
    logger.info("Transforming sale data (%s rows)", len(cleaned_sale_dataframe))

    transformed_sale_dataframe = transform_sale_data(cleaned_sale_dataframe)

    datalake_service.upload_as_parquet(
        dataframe=transformed_sale_dataframe,
        bucket_name=config.DATALAKE_BUCKET_NAME,
        object_key=config.TRANSFORMED_SALE_DATA_DATALAKE_PATH,
    )


def store_sale_data_to_oltp() -> None:
    datalake_service = SaleDataLakeService()
    sale_dataframe = datalake_service.read_parquet(
        bucket_name=config.DATALAKE_BUCKET_NAME,
        object_key=config.TRANSFORMED_SALE_DATA_DATALAKE_PATH,
    )

    database_service = DatabaseService()
    database_service.populate(sale_dataframe)


def store_sale_data_to_olap() -> None:
    datalake_service = SaleDataLakeService()
    sale_dataframe = datalake_service.read_parquet(
        bucket_name=config.DATALAKE_BUCKET_NAME,
        object_key=config.TRANSFORMED_SALE_DATA_DATALAKE_PATH,
    )

    sale_fact_dataframe = transform_sale_fact(sale_dataframe)

    sale_fact_service = SaleFactService()
    sale_fact_service.populate(sale_fact_dataframe)


def generate_sale_reports() -> None:
    sale_fact_service = SaleFactService()

    logger.info("Revenue by category: %s", sale_fact_service.revenue_by_category())
    logger.info("Revenue by country: %s", sale_fact_service.revenue_by_country())
    logger.info("Sale ETL pipeline finished successfully.")


with DAG(dag_id="sale_etl_pipeline", schedule=None, catchup=False, ) as dag:
    load_task = PythonOperator( task_id="load_sale_data",  python_callable=read_sale_data,)
    clean_task = PythonOperator(task_id="clean_sale_data", python_callable=clean_sale_data_task,)
    transform_task = PythonOperator( task_id="transform_sale_data", python_callable=transform_sale_data_task,)
    store_oltp_task = PythonOperator(  task_id="store_sale_data_to_oltp",  python_callable=store_sale_data_to_oltp, )
    store_olap_task = PythonOperator( task_id="store_sale_data_to_olap", python_callable=store_sale_data_to_olap,)
    report_task = PythonOperator( task_id="generate_sale_reports", python_callable=generate_sale_reports,)

    load_task >> clean_task >> transform_task
    transform_task >> store_oltp_task
    transform_task >> store_olap_task
    store_oltp_task >> report_task
    store_olap_task >> report_task
