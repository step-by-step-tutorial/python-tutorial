
import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def given_sale_spark_session() -> SparkSession:
    given_sale_spark_session_instance = (
        SparkSession.builder
        .master("local[2]")
        .appName("sale-etl-platform-tests")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )

    yield given_sale_spark_session_instance

    given_sale_spark_session_instance.stop()
