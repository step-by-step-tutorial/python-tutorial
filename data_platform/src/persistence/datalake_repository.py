from __future__ import annotations

import logging
from io import BytesIO
from uuid import uuid4

import pandas as pd

from dataset.definition import DataLakeEndpoint

logger = logging.getLogger(__name__)


class DataLakeRepository:
    def __init__(self, endpoint: DataLakeEndpoint) -> None:
        self.endpoint = endpoint
        self.connection_name = endpoint.connection_name
        self.bucket_name = endpoint.bucket_name

    def _list_object_keys(self, relative_path: str) -> list[str]:
        from connector.datalake_connection_factory import get_connection

        client = get_connection(self.connection_name)
        response = client.list_objects_v2(Bucket=self.bucket_name, Prefix=relative_path.strip("/"))

        return [object_metadata["Key"] for object_metadata in response.get("Contents", [])]

    def upload(
        self,
        df: pd.DataFrame,
        relative_path: str,
        file_extension: str = "parquet",
    ) -> str:
        from connector.datalake_connection_factory import get_connection

        parquet_buffer = BytesIO()
        df.to_parquet(parquet_buffer, index=False)
        parquet_buffer.seek(0)

        object_key = f"{relative_path.strip('/')}/part-{uuid4()}.{file_extension}"
        logger.info("Upload a %s file in bucket %s with path %s", file_extension, self.bucket_name, object_key)

        client = get_connection(self.connection_name)
        response = client.list_buckets()
        bucket_names = [bucket["Name"] for bucket in response.get("Buckets", [])]
        if self.bucket_name not in bucket_names:
            client.create_bucket(Bucket=self.bucket_name)

        client.put_object(Bucket=self.bucket_name, Key=object_key, Body=parquet_buffer)

        return object_key

    def download(self, relative_path: str, file_extension: str = "parquet") -> pd.DataFrame:
        logger.info("Download all %s files from bucket %s with path %s", file_extension, self.bucket_name, relative_path)
        dataframes: list[pd.DataFrame] = []
        from connector.datalake_connection_factory import get_connection

        client = get_connection(self.connection_name)

        for object_key in self._list_object_keys(relative_path):
            if not object_key.endswith(f".{file_extension}"):
                continue

            parquet_buffer = BytesIO()
            client.download_fileobj(self.bucket_name, object_key, parquet_buffer)
            parquet_buffer.seek(0)
            dataframes.append(pd.read_parquet(parquet_buffer))

        if not dataframes:
            raise FileNotFoundError(f"No {file_extension} files found under path: {relative_path}")

        return pd.concat(dataframes, ignore_index=True)
