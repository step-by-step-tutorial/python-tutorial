from __future__ import annotations

from io import BytesIO

import pandas as pd

from dataset.definition import DataLakeEndpoint


class DataLakeIngestor:
    def __init__(self, endpoint: DataLakeEndpoint) -> None:
        self.endpoint = endpoint

    def ingest(self) -> pd.DataFrame:
        if not self.endpoint.relative_path:
            raise ValueError("relative_path is required")

        from connector.datalake_connection_factory import get_connection

        dataframes: list[pd.DataFrame] = []
        client = get_connection(self.endpoint.connection_name)
        response = client.list_objects_v2(Bucket=self.endpoint.bucket_name, Prefix=self.endpoint.relative_path.strip("/"))

        for object_metadata in response.get("Contents", []):
            object_key = object_metadata["Key"]
            if not object_key.endswith(".parquet"):
                continue
            parquet_buffer = BytesIO()
            client.download_fileobj(self.endpoint.bucket_name, object_key, parquet_buffer)
            parquet_buffer.seek(0)
            dataframes.append(pd.read_parquet(parquet_buffer))

        if not dataframes:
            raise FileNotFoundError(f"No parquet files found under path: {self.endpoint.relative_path}")

        return pd.concat(dataframes, ignore_index=True)
