from __future__ import annotations

from io import BytesIO

import pandas as pd

from connector.datalake_connection_factory import get_connection


class HouseDataLakeIngestor:
    def __init__(self, bucket_name: str, relative_path: str) -> None:
        self.bucket_name = bucket_name
        self.relative_path = relative_path

    def ingest(self) -> pd.DataFrame:
        dataframes = []
        client = get_connection("house.datalake")
        response = client.list_objects_v2(Bucket=self.bucket_name, Prefix=self.relative_path.strip("/"))

        for object_metadata in response.get("Contents", []):
            object_key = object_metadata["Key"]
            if not object_key.endswith(".parquet"):
                continue
            parquet_buffer = BytesIO()
            client.download_fileobj(self.bucket_name, object_key, parquet_buffer)
            parquet_buffer.seek(0)
            dataframes.append(pd.read_parquet(parquet_buffer))

        if not dataframes:
            raise FileNotFoundError(f"No parquet files found under path: {self.relative_path}")

        return pd.concat(dataframes, ignore_index=True)
