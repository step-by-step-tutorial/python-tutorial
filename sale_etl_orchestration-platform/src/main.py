import logging

import config
from clean_sale_data_util import clean_sale_data
from datalake_service import DataLakeService
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


def main() -> None:
    logger.info("Loading sale data from: %s", config.RAW_SALE_DATA_FILE_PATH)
    sale_df = read_csv(config.RAW_SALE_DATA_FILE_PATH)

    logger.info("Cleaning sale data (%s rows)", len(sale_df))
    sale_df = clean_sale_data(sale_df)

    logger.info("Transforming sale data (%s rows)", len(sale_df))
    sale_df = transform_sale_data(sale_df)

    logger.info("Storing data into OLTP (PostgreSQL)")
    database_service = DatabaseService()
    populate(sale_df)

    logger.info("Storing cleaned Parquet to Data Lake")
    datalake_service = DataLakeService()
    datalake_service.upload_as_parquet(
        dataframe=sale_df,
        bucket_name=config.DATALAKE_BUCKET_NAME,
        object_key=config.CLEANED_SALE_DATA_DATALAKE_PATH,
    )

    logger.info("Storing data into OLAP (ClickHouse)")
    sale_fact_df = transform_sale_fact(sale_df)
    sale_fact_service = SaleFactService()
    sale_fact_service.populate(sale_fact_df)

    logger.info("Revenue by category:")
    print(sale_fact_service.revenue_by_category())

    logger.info("Revenue by country:")
    print(sale_fact_service.revenue_by_country())

    logger.info("Sale ETL pipeline finished successfully.")


if __name__ == "__main__":
    main()
