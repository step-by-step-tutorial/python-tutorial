from os import getenv
from pathlib import Path

PROJECT_ROOT = Path(getenv("PROJECT_ROOT", Path(__file__).resolve().parents[3])).resolve()
CONFIG_DIR = Path(getenv("CONFIG_DIR", Path(PROJECT_ROOT, "config"))).resolve()
OUTPUT_DIR = Path(getenv("OUTPUT_DIR", Path(PROJECT_ROOT, "output"))).resolve()
DATABASE_URL = getenv("DATABASE_URL", "postgresql+psycopg2://admin:admin@localhost:5432/app_database")
DATABASE_SCHEMA = getenv("DATABASE_SCHEMA", "test_data")
KAFKA_BOOTSTRAP_SERVERS = getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_FLUSH_TIMEOUT_SECONDS = float(getenv("KAFKA_FLUSH_TIMEOUT_SECONDS", "5"))
RANDOM_SEED = 42
