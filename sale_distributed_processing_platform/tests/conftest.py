import pytest
from pyspark.sql import SparkSession


APP_NAME = "Tutorial: Establish Test Connection"
MASTER_URL = "local[*]"


@pytest.fixture(scope="session")
def given_sale_spark_session() -> SparkSession:
    session = SparkSession.builder \
            .appName(APP_NAME) \
            .master(MASTER_URL) \
            .getOrCreate()

    yield session
    session.stop()
