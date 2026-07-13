import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_DIR = Path(os.getenv("DATA_DIR", PROJECT_ROOT / "data"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", PROJECT_ROOT / "output"))

RAW_SALE_DATA_FILE_PATH = Path(INPUT_DIR / "sale_data.csv")
RAW_SALE_DATA_DATALAKE_PATH = "raw/sale/raw_sale_data.parquet"
CLEANED_SALE_DATA_DATALAKE_PATH = "cleaned/sale/cleaned_sale_data.parquet"
TRANSFORMED_SALE_DATA_DATALAKE_PATH = "transformed/sale/transformed_sale_data.parquet"

POSTGRES_URL = os.getenv("POSTGRES_URL","postgresql+psycopg2://admin:admin@localhost:5432/sale_oltp",)

DATALAKE_ENDPOINT = os.getenv("DATALAKE_ENDPOINT", "http://localhost:9000")
DATALAKE_ACCESS_KEY = os.getenv("DATALAKE_ACCESS_KEY", "admin")
DATALAKE_SECRET_KEY = os.getenv("DATALAKE_SECRET_KEY", "administrator")
DATALAKE_BUCKET_NAME = os.getenv("DATALAKE_BUCKET_NAME", "sale-datalake")

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", "8123"))
CLICKHOUSE_DATABASE = os.getenv("CLICKHOUSE_DATABASE", "sale_warehouse")
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "admin")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "admin")
