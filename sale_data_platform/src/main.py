import config
from csv_utils import read_csv
from cleaner_utils import clean_sales_data
from transformer import transform_sales_data, build_warehouse_dataframe
from database_service import DatabaseService
from data_lake_service import DataLakeService
from fact_sales_service import FactSalesService


def main() -> None:
    print("Loading data")
    df = read_csv(config.CSV_PATH)

    print("Cleaning data")
    df = clean_sales_data(df)

    print("Transforming data")
    df = transform_sales_data(df)

    print("Storing data into OLTP (PostgreSQL)")
    database_service = DatabaseService(config.POSTGRES_URL)
    database_service.populate(df)

    print("Storing cleaned Parquet to Data Lake (MinIO)")
    data_lake_service = DataLakeService(
        endpoint=config.MINIO_ENDPOINT,
        access_key=config.MINIO_ACCESS_KEY,
        secret_key=config.MINIO_SECRET_KEY,
        bucket_name=config.MINIO_BUCKET,
    )

    data_lake_service.upload_parquet(
        df=df,
        object_path=config.PARQUET_PATH,
        object_key="cleaned/sales/cleaned_sales_data.parquet",
    )

    print("Storing data into OLAP (ClickHouse)")
    fact_sales_service = FactSalesService(
        host=config.CLICKHOUSE_HOST,
        port=config.CLICKHOUSE_PORT,
        username=config.CLICKHOUSE_USER,
        password=config.CLICKHOUSE_PASSWORD,
    )

    warehouse_df = build_warehouse_dataframe(df)
    fact_sales_service.populate_fact_sales(warehouse_df)

    print("Revenue by category:")
    print(fact_sales_service.revenue_by_category())

    print("Revenue by country:")
    print(fact_sales_service.revenue_by_country())

    print("Program finished successfully.")


if __name__ == "__main__":
    main()
