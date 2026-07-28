import os
from pathlib import Path

import time

RESOURCES_DIR = os.getenv("RESOURCES_DIR", "resources")
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "output"))
SCRIPTS_DIR = Path(os.getenv("SCRIPTS_DIR", "scripts"))

DATA_FILE = f"{RESOURCES_DIR}/{os.getenv("DATA_FILE", "data.csv")}"

SPARK_APPLICATION_NAME = os.getenv("SPARK_APPLICATION_NAME", "SALE_DISTRIBUTED_PROCESSING_PLATFORM")
SPARK_MASTER_URL = os.getenv("SPARK_MASTER_URL", "local[*]")
SPARK_DRIVER_HOST = os.getenv("SPARK_DRIVER_HOST", "127.0.0.1")
SPARK_DRIVER_BIND_ADDRESS = os.getenv("SPARK_DRIVER_BIND_ADDRESS", "127.0.0.1")

DATABASE_URL = os.getenv("DATABASE_URL", "jdbc:postgresql://localhost:5432/sale_database")
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = int(os.getenv("DATABASE_PORT", "5432"))
DATABASE_NAME = os.getenv("DATABASE_NAME", "sale_database")
DATABASE_USER = os.getenv("DATABASE_USER", "admin")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "admin")
DATABASE_DRIVER = os.getenv("DATABASE_DRIVER", "org.postgresql.Driver")
DATABASE_SALE_STAGE_TABLE = "sale_stage"

DATALAKE_ENDPOINT = os.getenv("DATALAKE_ENDPOINT", "http://localhost:9000")
DATALAKE_ACCESS_KEY = os.getenv("DATALAKE_ACCESS_KEY", "admin")
DATALAKE_SECRET_KEY = os.getenv("DATALAKE_SECRET_KEY", "administrator")
DATALAKE_BUCKET_NAME = os.getenv("DATALAKE_BUCKET_NAME", "sale-datalake")

DATAWAREHOUSE_HOST = os.getenv("DATAWAREHOUSE_HOST", "localhost")
DATAWAREHOUSE_PORT = int(os.getenv("DATAWAREHOUSE_PORT", "8123"))
DATAWAREHOUSE_NAME = os.getenv("DATAWAREHOUSE_NAME", "sale_datawarehouse")
DATAWAREHOUSE_USER = os.getenv("DATAWAREHOUSE_USER", "admin")
DATAWAREHOUSE_PASSWORD = os.getenv("DATAWAREHOUSE_PASSWORD", "admin")


def build_sale_datalake_output_uri() -> str:
    return f"s3a://{DATALAKE_BUCKET_NAME}/{OUTPUT_DIR}/{time.time()}"
