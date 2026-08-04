import logging
from datetime import UTC, datetime

import pandas as pd
from itables import show

from app_config import env_config as ec
from service import csv_sale_service, database_sale_service, datalake_sale_service, datawarehouse_sale_service
from util.datalake_utils import DatalakeLayer, build_sale_datalake_path

logger = logging.getLogger(__name__)


def run() -> None:
    ingestion_time = datetime.now(UTC)

    draw_line()
    logger.info("Starting sale pipeline with ingestion time %s", ingestion_time)

    raw_sale_data_path = upload_raw_sale_data(ingestion_time)
    draw_line()

    cleaned_sale_data_path = clean_sale_data(raw_sale_data_path, ingestion_time)
    draw_line()

    enriched_sale_data_path = enrich_sale_data(cleaned_sale_data_path, ingestion_time)
    draw_line()

    enriched_dataframe = read_enriched_sale_data(enriched_sale_data_path)

    populate_database(enriched_dataframe)
    draw_line()

    populate_datawarehouse(enriched_dataframe)
    draw_line()

    show_enriched_sale_data(enriched_dataframe)
    draw_line()

    process_data_by_csv(enriched_dataframe)
    draw_line()

    process_data_by_datawarehouse()
    draw_line()


def upload_raw_sale_data(ingestion_time: datetime) -> str:
    raw_sale_data_path = build_sale_datalake_path(layer=DatalakeLayer.RAW, ingestion_time=ingestion_time)

    logger.info("Reading sale data from %s", ec.DATA_FILE)
    dataframe = csv_sale_service.read_data(file_name=ec.DATA_FILE)

    logger.info("Uploading raw sale data to %s", raw_sale_data_path)
    datalake_sale_service.upload_parquet(dataframe=dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME,
                                         path=raw_sale_data_path)

    return raw_sale_data_path


def clean_sale_data(raw_sale_data_path: str, ingestion_time: datetime) -> str:
    cleaned_sale_data_path = build_sale_datalake_path(layer=DatalakeLayer.CLEANED, ingestion_time=ingestion_time)

    logger.info("Reading raw sale data from %s", raw_sale_data_path)
    dataframe = datalake_sale_service.download_parquet(bucket_name=ec.DATALAKE_BUCKET_NAME, path=raw_sale_data_path)

    logger.info("Cleaning sale data")
    cleaned_dataframe = csv_sale_service.clean_data(dataframe)

    logger.info("Uploading cleaned sale data to %s", cleaned_sale_data_path)
    datalake_sale_service.upload_parquet(dataframe=cleaned_dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME,
                                         path=cleaned_sale_data_path)

    return cleaned_sale_data_path


def enrich_sale_data(cleaned_sale_data_path: str, ingestion_time: datetime) -> str:
    enriched_sale_data_path = build_sale_datalake_path(layer=DatalakeLayer.ENRICHED, ingestion_time=ingestion_time)

    logger.info("Reading cleaned sale data from %s", cleaned_sale_data_path)
    dataframe = datalake_sale_service.download_parquet(bucket_name=ec.DATALAKE_BUCKET_NAME, path=cleaned_sale_data_path)

    logger.info("Enriching sale data")
    enriched_dataframe = csv_sale_service.enrich_data(dataframe)

    logger.info("Uploading enriched sale data to %s", enriched_sale_data_path)
    datalake_sale_service.upload_parquet(dataframe=enriched_dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME,
                                         path=enriched_sale_data_path)

    return enriched_sale_data_path


def read_enriched_sale_data(enriched_sale_data_path: str) -> pd.DataFrame:
    logger.info("Reading enriched sale data from %s", enriched_sale_data_path)
    return datalake_sale_service.download_parquet(bucket_name=ec.DATALAKE_BUCKET_NAME, path=enriched_sale_data_path)


def populate_database(enriched_dataframe: pd.DataFrame) -> None:
    logger.info("Populating database")
    database_sale_service.populate(enriched_dataframe)


def populate_datawarehouse(enriched_dataframe: pd.DataFrame) -> None:
    logger.info("Populating data warehouse")
    datawarehouse_sale_service.populate(enriched_dataframe)


def show_enriched_sale_data(enriched_dataframe: pd.DataFrame) -> None:
    logger.info("Showing enriched sale data")
    show(enriched_dataframe)


def process_data_by_csv(enriched_dataframe: pd.DataFrame) -> None:
    logger.info("Processing data by CSV service")

    logger.info("Calculating revenue by category")
    revenue_by_category_dataframe = csv_sale_service.get_revenue_by_category(enriched_dataframe)
    show(revenue_by_category_dataframe)

    logger.info("Calculating revenue by country")
    revenue_by_country_dataframe = csv_sale_service.get_revenue_by_country(enriched_dataframe)
    show(revenue_by_country_dataframe)


def process_data_by_datawarehouse() -> None:
    logger.info("Processing data by Datawarehouse")

    logger.info("Calculating revenue by category")
    revenue_by_category_dataframe = datawarehouse_sale_service.get_revenue_by_category()
    show(revenue_by_category_dataframe)

    logger.info("Calculating revenue by country")
    revenue_by_country_dataframe = datawarehouse_sale_service.get_revenue_by_country()
    show(revenue_by_country_dataframe)


def draw_line() -> None:
    logger.info(100 * "=")
