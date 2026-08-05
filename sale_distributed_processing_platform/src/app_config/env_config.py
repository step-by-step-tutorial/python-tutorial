import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RESOURCES_DIR = os.getenv("RESOURCES_DIR", "resources")
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "output"))
SCRIPTS_DIR = Path(os.getenv("SCRIPTS_DIR", "scripts"))
SPARK_DIR = Path(os.getenv("SPARK_DIR", "spark"))
ML_MODEL_PATH = Path(os.getenv("ML_MODEL_PATH", "models/sale_model.joblib"))
DL_MODEL_PATH = Path(os.getenv("DL_MODEL_PATH", "models/sale_neural_network.pt"))

DATA_FILE = os.getenv("DATA_FILE", "data.csv")

SPARK_APPLICATION_NAME = os.getenv("SPARK_APPLICATION_NAME", "SALE_DISTRIBUTED_PROCESSING_PLATFORM")
SPARK_MASTER_URL = os.getenv("SPARK_MASTER_URL", "local[*]")
SPARK_DRIVER_HOST = os.getenv("SPARK_DRIVER_HOST", "127.0.0.1")
SPARK_DRIVER_BIND_ADDRESS = os.getenv("SPARK_DRIVER_BIND_ADDRESS", "127.0.0.1")

DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = int(os.getenv("DATABASE_PORT", "5432"))
DATABASE_NAME = os.getenv("DATABASE_NAME", "sale_database")
DATABASE_USER = os.getenv("DATABASE_USER", "admin")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "admin")
DATABASE_DRIVER = os.getenv("DATABASE_DRIVER", "org.postgresql.Driver")
DATABASE_JDBC_URL = os.getenv("DATABASE_JDBC_URL", f"jdbc:postgresql://{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}")
DATABASE_SQLALCHEMY_URL = os.getenv("DATABASE_SQLALCHEMY_URL",
                                    f"postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}")
DATABASE_STAGE_TABLE_NAME = "sale_stage"

DATALAKE_ENDPOINT = os.getenv("DATALAKE_ENDPOINT", "http://localhost:9000")
DATALAKE_ACCESS_KEY = os.getenv("DATALAKE_ACCESS_KEY", "admin")
DATALAKE_SECRET_KEY = os.getenv("DATALAKE_SECRET_KEY", "administrator")
DATALAKE_BUCKET_NAME = os.getenv("DATALAKE_BUCKET_NAME", "sale-datalake")
DATALAKE_SCHEME = os.getenv("DATALAKE_SCHEME", "s3a")
DATALAKE_ENVIRONMENT = os.getenv("DATALAKE_ENVIRONMENT", "dev")
DATALAKE_SALE_DATASET = os.getenv("DATALAKE_SALE_DATASET", "sale")

DATAWAREHOUSE_HOST = os.getenv("DATAWAREHOUSE_HOST", "localhost")
DATAWAREHOUSE_PORT = int(os.getenv("DATAWAREHOUSE_PORT", "8123"))
DATAWAREHOUSE_NAME = os.getenv("DATAWAREHOUSE_NAME", "sale_datawarehouse")
DATAWAREHOUSE_USER = os.getenv("DATAWAREHOUSE_USER", "admin")
DATAWAREHOUSE_PASSWORD = os.getenv("DATAWAREHOUSE_PASSWORD", "admin")

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "sale-events")

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")


def resolve(path: Path) -> Path:
    return PROJECT_ROOT / path
