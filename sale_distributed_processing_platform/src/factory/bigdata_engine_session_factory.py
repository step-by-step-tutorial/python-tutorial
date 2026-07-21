from pyspark.sql import SparkSession

from app_config import env_config as ec

SPARK_JARS = [
    "org.postgresql:postgresql:42.7.7",
    "org.apache.hadoop:hadoop-aws:3.4.1",
    "software.amazon.awssdk:bundle:2.31.65",
]


def create_session() -> SparkSession | None:
    try:
        session = SparkSession.builder \
            .appName(ec.SPARK_APPLICATION_NAME) \
            .master(ec.SPARK_MASTER_URL) \
            .config("spark_tutorial.driver.host", ec.SPARK_DRIVER_HOST) \
            .config("spark_tutorial.driver.bindAddress", ec.SPARK_DRIVER_BIND_ADDRESS) \
            .config("spark.jars.packages", ",".join(SPARK_JARS), ) \
            .config("spark.hadoop.fs.s3a.endpoint", ec.DATALAKE_ENDPOINT, ) \
            .config("spark.hadoop.fs.s3a.access.key", ec.DATALAKE_ACCESS_KEY, ) \
            .config("spark.hadoop.fs.s3a.secret.key", ec.DATALAKE_SECRET_KEY, ) \
            .config("spark.hadoop.fs.s3a.path.style.access", "true", ) \
            .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false", ) \
            .getOrCreate()
        print(f"Spark version: {session.version}")
        print(f"Application [{ec.SPARK_APPLICATION_NAME}] established a connection to Spark at [{ec.SPARK_DRIVER_HOST}]")
        return session
    except Exception as e:
        print(
            f"Application [{ec.SPARK_APPLICATION_NAME}] could not established a connection to Spark at [{ec.SPARK_DRIVER_HOST}] due to {str(e)}")
        return None
