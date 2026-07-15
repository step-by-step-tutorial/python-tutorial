
import sys

from pyspark.sql import SparkSession

from src import config


class SaleSparkSessionService:
    def create_sale_spark_session(self) -> SparkSession:
        return (
            SparkSession.builder
            .appName(config.APPLICATION_NAME)
            .master(config.SPARK_MASTER_URL)
            .config("spark.pyspark.python", sys.executable)
            .config("spark.pyspark.driver.python", sys.executable)
            .config("spark.executorEnv.PYSPARK_PYTHON", sys.executable)
            .config("spark.executorEnv.PYSPARK_DRIVER_PYTHON", sys.executable)
            .config("spark.python.use.daemon", "false")
            .config(
                "spark.jars.packages",
                ",".join(
                    [
                        "org.postgresql:postgresql:42.7.7",
                        "org.apache.hadoop:hadoop-aws:3.4.1",
                        "software.amazon.awssdk:bundle:2.31.65",
                    ]
                ),
            )
            .config(
                "spark.hadoop.fs.s3a.endpoint",
                config.DATA_LAKE_ENDPOINT,
            )
            .config(
                "spark.hadoop.fs.s3a.access.key",
                config.DATA_LAKE_ACCESS_KEY,
            )
            .config(
                "spark.hadoop.fs.s3a.secret.key",
                config.DATA_LAKE_SECRET_KEY,
            )
            .config(
                "spark.hadoop.fs.s3a.path.style.access",
                "true",
            )
            .config(
                "spark.hadoop.fs.s3a.connection.ssl.enabled",
                "false",
            )
            .getOrCreate()
        )
