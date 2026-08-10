import logging

import pyspark.sql as spark

from app_config import env_config as ec
from util.string_utils import should_be_not_none, should_be_not_none_or_empty

logger = logging.getLogger(__name__)


def overwrite(dataframe: spark.DataFrame, bucket_name: str, path: str) -> None:
    should_be_not_none(dataframe, "dataframe")
    should_be_not_none_or_empty(bucket_name, "bucket_name")
    should_be_not_none_or_empty(path, "path")
    logger.info("Write data to %s", path)

    dataframe.write.mode("overwrite").parquet(build_path(bucket_name, path))


def read(session: spark.SparkSession, bucket_name: str, path: str) -> spark.DataFrame:
    should_be_not_none(session, "session")
    should_be_not_none_or_empty(bucket_name, "bucket_name")
    should_be_not_none_or_empty(path, "path")
    logger.info("Read data from %s", path)

    return session.read.parquet(build_path(bucket_name, path))


def append(dataframe: spark.DataFrame, bucket_name: str, path: str) -> None:
    should_be_not_none(dataframe, "dataframe")
    should_be_not_none_or_empty(bucket_name, "bucket_name")
    should_be_not_none_or_empty(path, "path")

    dataframe.write.mode("append").parquet(build_path(bucket_name, path))


def build_path(bucket_name: str, path: str) -> str:
    uri = f"{ec.DATALAKE_SCHEME}://{bucket_name.strip()}/{path.strip('/')}"
    return uri
