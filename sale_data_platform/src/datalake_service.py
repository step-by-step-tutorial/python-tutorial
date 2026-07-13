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
        return bucket_name not in bucket_names

    def create_bucket_if_not_exists(self, bucket_name: str) -> None:
        if self.bucket_is_exist(bucket_name):
            self.client.create_bucket(Bucket=bucket_name)

    def upload_as_parquet(self, dataframe: pd.DataFrame, bucket_name: str, object_key: str) -> None:
        self.create_bucket_if_not_exists(bucket_name)
        dataframe.to_parquet(config.CLEANED_SALE_DATA_LOCAL_FILE_PATH, index=False)
        self.client.upload_file(config.CLEANED_SALE_DATA_LOCAL_FILE_PATH, bucket_name, object_key)
