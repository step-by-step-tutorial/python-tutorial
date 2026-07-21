import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = Path(os.getenv("DATA_DIR", PROJECT_ROOT / "data"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", PROJECT_ROOT / "output"))
SQL_DIR = Path(os.getenv("SQL_DIR", PROJECT_ROOT / "scripts" / "query"))

RAW_SALE_DATA_FILE_PATH = os.getenv("RAW_SALE_DATA_FILE_PATH", INPUT_DIR / "sale_data.csv")

SPARK_APPLICATION_NAME = os.getenv("SPARK_APPLICATION_NAME", "sale-distributed-processing-platform")
SPARK_MASTER_URL = os.getenv("SPARK_MASTER_URL", "spark://localhost:7077")
SPARK_DRIVER_HOST = os.getenv("SPARK_DRIVER_HOST", "host.docker.internal")
SPARK_DRIVER_BIND_ADDRESS = os.getenv("SPARK_DRIVER_BIND_ADDRESS", "0.0.0.0")

DATABASE_URL = os.getenv("DATABASE_URL", "jdbc:postgresql://localhost:5432/sale_oltp")
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = int(os.getenv("DATABASE_PORT", "5432"))
DATABASE_NAME = os.getenv("DATABASE_NAME", "sale_oltp")
DATABASE_USER = os.getenv("DATABASE_USER", "admin")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "admin")
DATABASE_DRIVER = os.getenv("DATABASE_DRIVER", "org.postgresql.Driver")
DATABASE_SALE_STAGE_TABLE = "sale_stage"

DATALAKE_ENDPOINT = os.getenv("DATALAKE_ENDPOINT", "http://localhost:9000")
DATALAKE_ACCESS_KEY = os.getenv("DATALAKE_ACCESS_KEY", "admin")
DATALAKE_SECRET_KEY = os.getenv("DATALAKE_SECRET_KEY", "administrator")
DATALAKE_BUCKET_NAME = os.getenv("DATALAKE_BUCKET_NAME", "sale-data-lake")

DATAWAREHOUSE_HOST = os.getenv("DATAWAREHOUSE_HOST", "localhost")
DATAWAREHOUSE_HTTP_PORT = int(os.getenv("DATAWAREHOUSE_HTTP_PORT", "8123"))
DATAWAREHOUSE_DATABASE = os.getenv("DATAWAREHOUSE_DATABASE", "sale_warehouse")
DATAWAREHOUSE_USER = os.getenv("DATAWAREHOUSE_USER", "admin")
DATAWAREHOUSE_PASSWORD = os.getenv("DATAWAREHOUSE_PASSWORD", "admin")


def build_sale_datalake_output_uri() -> str:
    return (
        f"s3a://{DATALAKE_BUCKET_NAME}/"
        f"{OUTPUT_DIR}"
    )
