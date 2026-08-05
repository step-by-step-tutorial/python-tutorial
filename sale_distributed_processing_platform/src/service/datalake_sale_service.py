from io import BytesIO
from typing import Any
from uuid import uuid4

import pandas as pd
import pyspark.sql as spark

from app_config import env_config as ec
from factory import datalake_connection_factory
from util.datalake_utils import build_sale_datalake_path


def overwrite(dataframe: spark.DataFrame, bucket_name: str, path: str) -> None:
    if dataframe is None:
        raise ValueError("Cannot overwrite data because the dataframe is None.")

    if not bucket_name or not bucket_name.strip():
        raise ValueError("Cannot overwrite data because the bucket name is empty.")

    if not path or not path.strip():
        raise ValueError("Cannot overwrite data because the data lake path is empty.")

    uri = f"{ec.DATALAKE_SCHEME}://{bucket_name.strip()}/{path.strip('/')}"
    dataframe.write.mode("overwrite").parquet(uri)


def read(session: spark.SparkSession, bucket_name: str, path: str) -> spark.DataFrame:
    if session is None:
        raise ValueError("Cannot read data because the Spark session is None.")

    if not bucket_name or not bucket_name.strip():
        raise ValueError("Cannot read data because the bucket name is empty.")

    if not path or not path.strip():
        raise ValueError("Cannot read data because the data lake path is empty.")

    uri = f"{ec.DATALAKE_SCHEME}://{bucket_name.strip()}/{path.strip('/')}"
    return session.read.parquet(uri)


def append(dataframe: spark.DataFrame, bucket_name: str, path: str) -> None:
    if dataframe is None:
        raise ValueError("Cannot append data because the input DataFrame is None.")
    if bucket_name is None:
        raise ValueError("Cannot append data because the bucket name is None.")
    if path is None:
        raise ValueError("Cannot append data because the input path is None.")
    uri = f"{ec.DATALAKE_SCHEME}://{bucket_name.strip()}/{path.strip('/')}"
    (
        dataframe.write
        .mode("append")
        .parquet(uri)
    )


def get_bucket_names(client: Any) -> list[str]:
    buckets = client.list_buckets().get("Buckets", [])
    return [bucket["Name"] for bucket in buckets]


def bucket_list() -> list[str]:
    with datalake_connection_factory.create_connection() as client:
        return get_bucket_names(client)


def bucket_exists(bucket_name: str) -> bool:
    with datalake_connection_factory.create_connection() as client:
        return bucket_name in get_bucket_names(client)


def create_bucket_if_not_exists(bucket_name: str) -> None:
    with datalake_connection_factory.create_connection() as client:
        if bucket_name not in get_bucket_names(client):
            client.create_bucket(Bucket=bucket_name)


def upload_parquet(dataframe: pd.DataFrame, bucket_name: str, path: str) -> str:
    parquet_buffer = BytesIO()
    dataframe.to_parquet(parquet_buffer, index=False)
    parquet_buffer.seek(0)

    object_key = f"{path.strip('/')}/part-{uuid4()}.parquet"

    with datalake_connection_factory.create_connection() as client:
        if bucket_name not in get_bucket_names(client):
            client.create_bucket(Bucket=bucket_name)

        client.put_object(Bucket=bucket_name, Key=object_key, Body=parquet_buffer)

    return object_key


def download_parquet(bucket_name: str, path: str) -> pd.DataFrame:
    dataframes = []

    with datalake_connection_factory.create_connection() as client:
        response = client.list_objects_v2(Bucket=bucket_name, Prefix=path.strip("/"))

        for object_metadata in response.get("Contents", []):
            object_key = object_metadata["Key"]

            if not object_key.endswith(".parquet"):
                continue

            parquet_buffer = BytesIO()
            client.download_fileobj(bucket_name, object_key, parquet_buffer)
            parquet_buffer.seek(0)
            dataframes.append(pd.read_parquet(parquet_buffer))

    if not dataframes:
        raise FileNotFoundError(f"No Parquet files found under path: {path}")

    return pd.concat(dataframes, ignore_index=True)
