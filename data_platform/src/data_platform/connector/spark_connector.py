from pyspark.sql import SparkSession

from data_platform.config.key import Key
from data_platform.config.settings import settings

SPARK_JARS = [
    "org.postgresql:postgresql:42.7.7",
    "org.apache.hadoop:hadoop-aws:3.4.2",
    "org.slf4j:slf4j-api:1.7.36",
    "org.slf4j:slf4j-reload4j:1.7.36",
    "ch.qos.reload4j:reload4j:1.2.22",
    "org.apache.spark:spark-sql-kafka-0-10_2.13:4.1.2",
]


def _is_session_active(session: SparkSession) -> bool:
    try:
        spark_context = session.sparkContext
        jsc = getattr(spark_context, "_jsc", None)
        return jsc is not None and not jsc.sc().isStopped()
    except Exception:
        return False


def create_session() -> SparkSession:
    active_session = SparkSession.getActiveSession()
    if active_session is not None and _is_session_active(active_session):
        return active_session

    # A stopped JVM context can leave a stale session behind, so getOrCreate must not reuse it.
    SparkSession._instantiatedSession = None
    SparkSession._activeSession = None

    data_lake = settings.data_lake[Key.PLATFORM_DATA_LAKE]
    return (
        SparkSession.builder
        .appName(settings.spark.application_name)
        .master(settings.spark.master_url)
        .config("spark.driver.host", settings.spark.driver_host)
        .config("spark.driver.bindAddress", settings.spark.driver_bind_address)
        .config("spark.jars.packages", ",".join(SPARK_JARS))
        .config("spark.jars.ivy", "/opt/spark-ivy")
        .config("spark.jars.excludes", "org.slf4j:slf4j-api")
        .config("spark.hadoop.fs.s3a.endpoint", data_lake.endpoint)
        .config("spark.hadoop.fs.s3a.access.key", data_lake.access_key)
        .config("spark.hadoop.fs.s3a.secret.key", data_lake.secret_key)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        .config("spark.hadoop.fs.s3a.fast.upload", "true")
        .config("spark.hadoop.fs.s3a.fast.upload.buffer", settings.spark.buffer)
        .config("spark.hadoop.fs.s3a.fast.upload.active.blocks", settings.spark.active_blocks)
        .config("spark.hadoop.fs.s3a.threads.max", settings.spark.threads_max)
        .config("spark.hadoop.fs.s3a.max.total.tasks", settings.spark.max_total_tasks)
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.driver.extraJavaOptions",
                f"-XX:MaxDirectMemorySize={settings.spark.max_direct_memory_size}")
        .config("spark.executor.extraJavaOptions",
                f"-XX:MaxDirectMemorySize={settings.spark.max_direct_memory_size}")
        .getOrCreate()
    )
