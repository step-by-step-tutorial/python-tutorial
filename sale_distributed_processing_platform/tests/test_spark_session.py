from pyspark.sql import SparkSession

APP_NAME = "Test Application"
MASTER_URL = "spark://localhost:7077"
DRIVER_HOST = "host.docker.internal"
DRIVER_BIND_ADDRESS = "0.0.0.0"


def test_given_sale_spark_session():
    session = SparkSession.builder \
        .appName(APP_NAME) \
        .master(MASTER_URL) \
        .config("spark.driver.host", DRIVER_HOST) \
        .config("spark.driver.bindAddress", DRIVER_BIND_ADDRESS) \
        .getOrCreate()

    assert session is not None
    session.stop()
