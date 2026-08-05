from pathlib import Path

from pyspark.sql import SparkSession

from app_config import env_config as ec

SPARK_JARS = [
    "org.postgresql:postgresql:42.7.7",
    "org.apache.hadoop:hadoop-aws:3.4.2",
    "org.apache.logging.log4j:log4j-slf4j2-impl:2.24.3",
    "org.apache.spark:spark-sql-kafka-0-10_2.13:4.1.2"
]


def create_connection() -> SparkSession:
    Path(ec.S3A_BUFFER_DIR).mkdir(parents=True, exist_ok=True)
    try:
        session = (
            SparkSession.builder
            .appName(ec.SPARK_APPLICATION_NAME)
            .master(ec.SPARK_MASTER_URL)
            .config("spark.driver.host", ec.SPARK_DRIVER_HOST)
            .config("spark.driver.bindAddress", ec.SPARK_DRIVER_BIND_ADDRESS)
            .config("spark.jars.packages", ",".join(SPARK_JARS))
            .config("spark.hadoop.fs.s3a.endpoint", ec.DATALAKE_ENDPOINT)
            .config("spark.hadoop.fs.s3a.access.key", ec.DATALAKE_ACCESS_KEY)
            .config("spark.hadoop.fs.s3a.secret.key", ec.DATALAKE_SECRET_KEY)
            .config("spark.hadoop.fs.s3a.path.style.access", "true")
            .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
            .config("spark.hadoop.fs.s3a.fast.upload", "true")
            .config("spark.hadoop.fs.s3a.fast.upload.buffer", ec.SPARK_BUFFER)
            .config("spark.hadoop.fs.s3a.buffer.dir", ec.S3A_BUFFER_DIR)
            .config("spark.hadoop.fs.s3a.fast.upload.active.blocks", ec.SPARK_ACTIVE_BLOCKS)
            .config("spark.hadoop.fs.s3a.threads.max", ec.SPARK_THREADS_MAX)
            .config("spark.hadoop.fs.s3a.max.total.tasks", ec.SPARK_MAX_TOTAL_TASKS)
            .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
            .config("spark.driver.extraJavaOptions", f"-Dlog4j.configurationFile=file:{ec.SPARK_DIR}/log4j2.properties")
            .config("spark.executor.extraJavaOptions", f"-Dlog4j.configurationFile=file:{ec.SPARK_DIR}/log4j2.properties")
            .config("spark.driver.extraJavaOptions", f"-XX:MaxDirectMemorySize={ec.MAX_DIRECT_MEMORY_SIZE}")
            .config("spark.executor.extraJavaOptions", f"-XX:MaxDirectMemorySize={ec.MAX_DIRECT_MEMORY_SIZE}")
            .getOrCreate()
        )
        print(f"Spark version: {session.version}")
        print(
            f"Application [{ec.SPARK_APPLICATION_NAME}] established a connection to Spark at [{ec.SPARK_DRIVER_HOST}]")
        return session
    except Exception as e:
        print(
            f"Application [{ec.SPARK_APPLICATION_NAME}] could not established a connection to Spark at [{ec.SPARK_DRIVER_HOST}] due to {str(e)}")
        raise
