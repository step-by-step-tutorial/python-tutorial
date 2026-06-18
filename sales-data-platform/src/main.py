from src import config
from src.loader import load_csv
from src.cleaner import clean_sales_data
from src.transformer import transform_sales_data, build_warehouse_dataframe
from src.postgres_loader import PostgresLoader
from src.minio_loader import MinioLoader
from src.clickhouse_loader import ClickHouseLoader


def main() -> None:
    print("Loading CSV...")
    df = load_csv(config.CSV_PATH)

    print("Cleaning data...")
    df = clean_sales_data(df)

    print("Transforming data...")
    df = transform_sales_data(df)

    print("Loading OLTP data into PostgreSQL...")
    postgres_loader = PostgresLoader(config.POSTGRES_URL)
    postgres_loader.load(df)

    print("Uploading cleaned Parquet to MinIO Data Lake...")
    minio_loader = MinioLoader(
        endpoint=config.MINIO_ENDPOINT,
        access_key=config.MINIO_ACCESS_KEY,
        secret_key=config.MINIO_SECRET_KEY,
        bucket_name=config.MINIO_BUCKET,
    )

    minio_loader.upload_parquet(
        df=df,
        local_path=config.PARQUET_PATH,
        object_key="cleaned/sales/cleaned_sales_data.parquet",
    )

    print("Preparing warehouse dataframe...")
    warehouse_df = build_warehouse_dataframe(df)

    print("Loading OLAP data into ClickHouse...")
    clickhouse_loader = ClickHouseLoader(
        host=config.CLICKHOUSE_HOST,
        port=config.CLICKHOUSE_PORT,
        username=config.CLICKHOUSE_USER,
        password=config.CLICKHOUSE_PASSWORD,
    )

    clickhouse_loader.load_fact_sales(warehouse_df)

    print("Revenue by category:")
    print(clickhouse_loader.revenue_by_category())

    print("Revenue by country:")
    print(clickhouse_loader.revenue_by_country())

    print("Phase 2 pipeline finished successfully.")


if __name__ == "__main__":
    main()
