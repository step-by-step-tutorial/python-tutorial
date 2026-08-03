from io import BytesIO
from typing import Any

import pandas as pd
from pyspark.sql import DataFrame

from app_config import env_config as ec
from factory import datalake_connection_factory


def overwrite(dataframe: DataFrame) -> None:
    (
        dataframe.write
        .mode("overwrite")
        .partitionBy("year", "month", "country")
        .parquet(ec.build_sale_datalake_output_uri())
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


def upload_as_parquet(dataframe: pd.DataFrame, bucket_name: str, object_key: str) -> None:
    with datalake_connection_factory.create_connection() as client:
        if bucket_name not in get_bucket_names(client):
            client.create_bucket(Bucket=bucket_name)

        parquet_buffer = BytesIO()
        dataframe.to_parquet(parquet_buffer, index=False)
        parquet_buffer.seek(0)

        client.put_object(Bucket=bucket_name, Key=object_key, Body=parquet_buffer)


def read_parquet(bucket_name: str, object_key: str) -> pd.DataFrame:
    with datalake_connection_factory.create_connection() as client:
        parquet_buffer = BytesIO()
        client.download_fileobj(bucket_name, object_key, parquet_buffer)
        parquet_buffer.seek(0)
        return pd.read_parquet(parquet_buffer)
