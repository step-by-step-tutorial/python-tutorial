import logging
from io import BytesIO
from uuid import uuid4

import pandas as pd

from data_platform.model import DataLakeEndpoint
from data_platform.persistence.storage_repository import StorageRepository
from data_platform.registry.connection_registry import connection_registry

logger = logging.getLogger(__name__)


class DataLakeRepository(StorageRepository):
    def __init__(self, endpoint: DataLakeEndpoint) -> None:
        self._endpoint = endpoint
        self._connection_name = endpoint.connection_name
        self._bucket_name = endpoint.bucket_name

    def find_keys(self, relative_path: str) -> list[str]:
        client = connection_registry.get_item(self._connection_name)
        response = client.list_objects_v2(Bucket=self._bucket_name, Prefix=relative_path.strip("/"))

        return [object_metadata["Key"] for object_metadata in response.get("Contents", [])]

    def save(self, data: pd.DataFrame, path: str, file_extension: str = "parquet") -> str:
        parquet_buffer = BytesIO()
        data.to_parquet(parquet_buffer, index=False)
        parquet_buffer.seek(0)

        object_key = f"{path.strip('/')}/part-{uuid4()}.{file_extension}"
        client = connection_registry.get_item(self._connection_name)
        buckets = client.list_buckets()
        bucket_names = {bucket["Name"] for bucket in buckets.get("Buckets", [])}
        if self._bucket_name not in bucket_names:
            client.create_bucket(Bucket=self._bucket_name)
        client.put_object(Bucket=self._bucket_name, Key=object_key, Body=parquet_buffer)

        logger.info("Upload a %s file in bucket %s with path %s", file_extension, self._bucket_name, object_key)
        return object_key

    def create_bucket(self, bucket_name: str):
        client = connection_registry.get_item(self._connection_name)
        client.create_bucket(Bucket=bucket_name)

    def find(self, path: str, file_extension: str = "parquet") -> pd.DataFrame:

        dataframes: list[pd.DataFrame] = []
        client = connection_registry.get_item(self._connection_name)

        for object_key in self.find_keys(path):
            if not object_key.endswith(f".{file_extension}"):
                continue

            parquet_buffer = BytesIO()
            client.download_fileobj(self._bucket_name, object_key, parquet_buffer)
            parquet_buffer.seek(0)
            dataframes.append(pd.read_parquet(parquet_buffer))

        if not dataframes:
            raise FileNotFoundError(f"No {file_extension} files found under path: {path}")

        logger.info(f"Download all {file_extension} files from bucket {self._bucket_name} with path {path}")
        return pd.concat(dataframes, ignore_index=True)

