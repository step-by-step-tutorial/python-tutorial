from __future__ import annotations

import tempfile
from functools import lru_cache
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from pyspark.sql import SparkSession

from config.datalake import settings as datalake_settings
from config.spark import settings as spark_settings

SPARK_JARS = [
    "org.postgresql:postgresql:42.7.7",
    "org.apache.hadoop:hadoop-aws:3.4.2",
    "org.slf4j:slf4j-api:1.7.36",
    "org.slf4j:slf4j-reload4j:1.7.36",
    "ch.qos.reload4j:reload4j:1.2.22",
    "org.apache.spark:spark-sql-kafka-0-10_2.13:4.1.2",
]


def _source_root() -> Path:
    current_file = Path(__file__).resolve()
    for candidate in current_file.parents:
        if candidate.name == "src":
            return candidate

    return current_file.parents[2]


@lru_cache(maxsize=1)
def _build_source_archive() -> str:
    source_root = _source_root()
    archive_path = Path(tempfile.gettempdir()) / "data_platform_sources.zip"

    with ZipFile(archive_path, "w", compression=ZIP_DEFLATED) as archive:
        for path in source_root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix == ".pyc":
                continue
            if "__pycache__" in path.parts:
                continue

            archive.write(path, path.relative_to(source_root))

    return str(archive_path)


def create_session() -> SparkSession:
    session = (
        SparkSession.builder
        .appName(spark_settings.application_name)
        .master(spark_settings.master_url)
        .config("spark.driver.host", spark_settings.driver_host)
        .config("spark.driver.bindAddress", spark_settings.driver_bind_address)
        .config("spark.jars.packages", ",".join(SPARK_JARS))
        .config("spark.jars.excludes", "org.slf4j:slf4j-api")
        .config("spark.hadoop.fs.s3a.endpoint", datalake_settings.endpoint)
        .config("spark.hadoop.fs.s3a.access.key", datalake_settings.access_key)
        .config("spark.hadoop.fs.s3a.secret.key", datalake_settings.secret_key)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        .config("spark.hadoop.fs.s3a.fast.upload", "true")
        .config("spark.hadoop.fs.s3a.fast.upload.buffer", spark_settings.buffer)
        .config("spark.hadoop.fs.s3a.fast.upload.active.blocks", spark_settings.active_blocks)
        .config("spark.hadoop.fs.s3a.threads.max", spark_settings.threads_max)
        .config("spark.hadoop.fs.s3a.max.total.tasks", spark_settings.max_total_tasks)
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.driver.extraJavaOptions", f"-XX:MaxDirectMemorySize={spark_settings.max_direct_memory_size}")
        .config("spark.executor.extraJavaOptions", f"-XX:MaxDirectMemorySize={spark_settings.max_direct_memory_size}")
        .getOrCreate()
    )

    session.sparkContext.addPyFile(_build_source_archive())
    return session
