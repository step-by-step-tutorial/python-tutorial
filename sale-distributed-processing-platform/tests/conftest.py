
import os
import sys

import pytest
from pyspark.sql import SparkSession


os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)


@pytest.fixture(scope="session")
def given_sale_spark_session() -> SparkSession:
    given_sale_spark_session_instance = (
        SparkSession.builder
        .master("local[2]")
        .appName("sale-etl-platform-tests")
        .config("spark.pyspark.python", sys.executable)
        .config("spark.pyspark.driver.python", sys.executable)
        .config("spark.executorEnv.PYSPARK_PYTHON", sys.executable)
        .config("spark.executorEnv.PYSPARK_DRIVER_PYTHON", sys.executable)
        .config("spark.python.use.daemon", "false")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )

    yield given_sale_spark_session_instance

    given_sale_spark_session_instance.stop()
