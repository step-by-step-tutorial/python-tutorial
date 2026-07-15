import os

APPLICATION_NAME = os.getenv("APPLICATION_NAME", "sale-distributed-processing-platform", )

INPUT_CSV_PATH = os.getenv("INPUT_CSV_PATH", "data/sale_data.csv", )
CURATED_OUTPUT_PATH = os.getenv("CURATED_OUTPUT_PATH", "curated/sale", )

SPARK_MASTER_URL = os.getenv("SPARK_MASTER_URL", "local[*]", )

DATABASE_JDBC_URL = os.getenv("DATABASE_JDBC_URL", "jdbc:postgresql://localhost:5432/sale_oltp", )
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = int(os.getenv("DATABASE_PORT", "5432"))
DATABASE_DATABASE = os.getenv("DATABASE_DATABASE", "sale_oltp")
DATABASE_USER = os.getenv("DATABASE_USER", "admin")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "admin", )

DATA_LAKE_ENDPOINT = os.getenv("DATA_LAKE_ENDPOINT", "http://localhost:9000", )
DATA_LAKE_ACCESS_KEY = os.getenv("DATA_LAKE_ACCESS_KEY", "admin", )
DATA_LAKE_SECRET_KEY = os.getenv("DATA_LAKE_SECRET_KEY", "administrator", )
DATA_LAKE_BUCKET = os.getenv("DATA_LAKE_BUCKET", "sale-data-lake", )

WAREHOUSE_HOST = os.getenv("WAREHOUSE_HOST", "localhost")
WAREHOUSE_HTTP_PORT = int(os.getenv("WAREHOUSE_HTTP_PORT", "8123"))
WAREHOUSE_DATABASE = os.getenv("WAREHOUSE_DATABASE", "sale_warehouse", )
WAREHOUSE_USER = os.getenv("WAREHOUSE_USER", "admin", )
WAREHOUSE_PASSWORD = os.getenv("WAREHOUSE_PASSWORD", "admin", )


def build_sale_data_lake_output_uri() -> str:
    return (
        f"s3a://{DATA_LAKE_BUCKET}/"
        f"{CURATED_OUTPUT_PATH}"
    )
