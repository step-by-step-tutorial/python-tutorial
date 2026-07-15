
import os


SALE_APPLICATION_NAME = os.getenv(
    "SALE_APPLICATION_NAME",
    "sale-distributed-processing-platform",
)

SALE_SPARK_MASTER_URL = os.getenv(
    "SALE_SPARK_MASTER_URL",
    "local[*]",
)

SALE_INPUT_CSV_PATH = os.getenv(
    "SALE_INPUT_CSV_PATH",
    "data/sale.csv",
)

SALE_CURATED_OUTPUT_PATH = os.getenv(
    "SALE_CURATED_OUTPUT_PATH",
    "curated/sale",
)

SALE_POSTGRES_JDBC_URL = os.getenv(
    "SALE_POSTGRES_JDBC_URL",
    "jdbc:postgresql://localhost:5432/sale_oltp",
)

SALE_POSTGRES_HOST = os.getenv("SALE_POSTGRES_HOST", "localhost")
SALE_POSTGRES_PORT = int(os.getenv("SALE_POSTGRES_PORT", "5432"))
SALE_POSTGRES_DATABASE = os.getenv("SALE_POSTGRES_DATABASE", "sale_oltp")
SALE_POSTGRES_USER = os.getenv("SALE_POSTGRES_USER", "sale_platform_user")
SALE_POSTGRES_PASSWORD = os.getenv(
    "SALE_POSTGRES_PASSWORD",
    "sale_platform_password",
)

SALE_DATA_LAKE_ENDPOINT = os.getenv(
    "SALE_DATA_LAKE_ENDPOINT",
    "http://localhost:9000",
)
SALE_DATA_LAKE_ACCESS_KEY = os.getenv(
    "SALE_DATA_LAKE_ACCESS_KEY",
    "sale_data_lake_user",
)
SALE_DATA_LAKE_SECRET_KEY = os.getenv(
    "SALE_DATA_LAKE_SECRET_KEY",
    "sale_data_lake_password",
)
SALE_DATA_LAKE_BUCKET = os.getenv(
    "SALE_DATA_LAKE_BUCKET",
    "sale-data-lake",
)

SALE_WAREHOUSE_HOST = os.getenv("SALE_WAREHOUSE_HOST", "localhost")
SALE_WAREHOUSE_HTTP_PORT = int(
    os.getenv("SALE_WAREHOUSE_HTTP_PORT", "8123")
)
SALE_WAREHOUSE_DATABASE = os.getenv(
    "SALE_WAREHOUSE_DATABASE",
    "sale_warehouse",
)
SALE_WAREHOUSE_USER = os.getenv(
    "SALE_WAREHOUSE_USER",
    "sale_warehouse_user",
)
SALE_WAREHOUSE_PASSWORD = os.getenv(
    "SALE_WAREHOUSE_PASSWORD",
    "sale_warehouse_password",
)


def build_sale_data_lake_output_uri() -> str:
    return (
        f"s3a://{SALE_DATA_LAKE_BUCKET}/"
        f"{SALE_CURATED_OUTPUT_PATH}"
    )
