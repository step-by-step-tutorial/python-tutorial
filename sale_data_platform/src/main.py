import config
from file_utils import read_csv
from clean_sale_data_util import clean_sale_data
from transform_sale_data_util import transform_sale_data
from order_item_service import OrderItemService
from datalake_service import DataLakeService
from sale_fact_service import SaleFactService
from transform_sale_fact_util import transform_sale_fact


def main() -> None:
    print("Loading data")
    sale_data = read_csv(config.RAW_SALE_DATA_FILE_PATH)

    print("Cleaning data")
    sale_data = clean_sale_data(sale_data)

    print("Transforming data")
    sale_data = transform_sale_data(sale_data)

    print("Storing data into OLTP (PostgreSQL)")
    order_item_service = OrderItemService()
    order_item_service.populate(sale_data)

    print("Storing cleaned Parquet to Data Lake (MinIO)")
    datalake_service = DataLakeService()
    datalake_service.upload_as_parquet(
        dataframe=sale_data,
        bucket_name=config.DATALAKE_BUCKET_NAME,
        object_key=config.CLEANED_SALE_DATA_DATALAKE_PATH
    )

    print("Storing data into OLAP (ClickHouse)")
    sale_fact = transform_sale_fact(sale_data)
    sale_fact_service = SaleFactService()
    sale_fact_service.populate(sale_fact)

    print("Revenue by category:")
    print(sale_fact_service.revenue_by_category())

    print("Revenue by country:")
    print(sale_fact_service.revenue_by_country())

    print("Program finished successfully.")


if __name__ == "__main__":
    main()
