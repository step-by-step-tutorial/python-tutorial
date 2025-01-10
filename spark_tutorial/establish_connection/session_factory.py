from pyspark.sql import SparkSession

APP_NAME = "Tutorial: Establish Connection"
MASTER_URL = "spark://localhost:7077"
DRIVER_HOST = "host.docker.internal"
DRIVER_BIND_ADDRESS = "0.0.0.0"


def create_session() -> SparkSession | None:
    """
    Create and return a Spark session between local machine and dockerized instance of Spark.

    :return: Spark session
    :exception: SparkSession creation failed.
    """
    try:
        session = SparkSession.builder \
            .appName(APP_NAME) \
            .master(MASTER_URL) \
            .config("spark_tutorial.driver.host", DRIVER_HOST) \
            .config("spark_tutorial.driver.bindAddress", DRIVER_BIND_ADDRESS) \
            .getOrCreate()
        print(f"Application [{APP_NAME}] established a connection to Spark at [{DRIVER_HOST}]")
        return session
    except Exception as e:
        print(f"Application [{APP_NAME}] could not established a connection to Spark at [{DRIVER_HOST}] due to {str(e)}")
        return None
