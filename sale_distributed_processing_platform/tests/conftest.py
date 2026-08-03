import pytest
from pyspark.sql import SparkSession

APP_NAME = "Test Application"
MASTER_URL = "spark://localhost:7077"
DRIVER_HOST = "host.docker.internal"
DRIVER_BIND_ADDRESS = "0.0.0.0"


@pytest.fixture(scope="session")
def given_sale_spark_session() -> SparkSession:
    session = SparkSession.builder \
        .appName(APP_NAME) \
        .master(MASTER_URL) \
        .config("spark.driver.host", DRIVER_HOST) \
        .config("spark.driver.bindAddress", DRIVER_BIND_ADDRESS) \
        .getOrCreate()

    yield session
    session.stop()
