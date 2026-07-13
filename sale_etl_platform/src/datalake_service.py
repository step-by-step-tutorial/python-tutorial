from io import BytesIO
from typing import Any

import boto3
import pandas as pd

import config

STORAGE_SERVICE = "s3"


class DataLakeService:
    def __init__(self):
        self.client = boto3.client(
            STORAGE_SERVICE,
            endpoint_url=config.DATALAKE_ENDPOINT,
            aws_access_key_id=config.DATALAKE_ACCESS_KEY,
            aws_secret_access_key=config.DATALAKE_SECRET_KEY,
        )

    def bucket_list(self) -> list[Any]:
        buckets = self.client.list_buckets()["Buckets"]
        bucket_names = [bucket["Name"] for bucket in buckets]
        return bucket_names

    def bucket_is_exist(self, bucket_name: str) -> bool:
        bucket_names = self.bucket_list()
        return bucket_name in bucket_names

    def create_bucket_if_not_exists(self, bucket_name: str) -> None:
        if not self.bucket_is_exist(bucket_name):
            self.client.create_bucket(Bucket=bucket_name)

    def upload_as_parquet(
        self,
        dataframe: pd.DataFrame,
        bucket_name: str,
        object_key: str,
    ) -> None:
        self.create_bucket_if_not_exists(bucket_name)
        parquet_buffer = BytesIO()
        dataframe.to_parquet(parquet_buffer, index=False)
        parquet_buffer.seek(0)
        self.client.upload_fileobj(parquet_buffer, bucket_name, object_key)

    def read_parquet(self, bucket_name: str, object_key: str) -> pd.DataFrame:
        parquet_buffer = BytesIO()
        self.client.download_fileobj(bucket_name, object_key, parquet_buffer)
        parquet_buffer.seek(0)
        return pd.read_parquet(parquet_buffer)
