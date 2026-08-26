import logging
from io import BytesIO

import pandas as pd

from data_platform.model.endpoints import DataLakeEndpoint
from data_platform.registry.connection_registry import connection_registry
from data_platform.repository.storage_repository import StorageRepository
from data_platform.util.path_utils import generate_data_object_key, normalize_relative_path

logger = logging.getLogger(__name__)


class DataLakeRepository(StorageRepository):
    def __init__(self, endpoint: DataLakeEndpoint) -> None:
        self._endpoint = endpoint
        self._connection_name = endpoint.connection_name
        self._bucket_name = endpoint.bucket_name

    def write(self, data: pd.DataFrame, path: str, file_extension: str = "parquet") -> str:
        row_count = len(data) if isinstance(data, pd.DataFrame) else "unknown"
        column_count = len(data.columns) if isinstance(data, pd.DataFrame) else "unknown"
        logger.info("Writing datalake data: bucket=%s path=%s rows=%s columns=%s", self._bucket_name, path, row_count, column_count)
        parquet_buffer = BytesIO()
        data.to_parquet(parquet_buffer, index=False)
        parquet_buffer.seek(0)

        object_key = generate_data_object_key(path, file_extension)
        client = connection_registry.get_item(self._connection_name)
        client.put_object(Bucket=self._bucket_name, Key=object_key, Body=parquet_buffer)

        logger.info("Upload a %s file in bucket %s with path %s", file_extension, self._bucket_name, object_key)
        return object_key

    def read(self, path: str, file_extension: str = "parquet") -> pd.DataFrame:
        client = connection_registry.get_item(self._connection_name)
        dataframes: list[pd.DataFrame] = []
        object_keys = self.find_keys(path)
        logger.info("Reading datalake data: bucket=%s path=%s objects=%s", self._bucket_name, path, len(object_keys))

        for object_key in object_keys:
            parquet_buffer = BytesIO()
            client.download_fileobj(self._bucket_name, object_key, parquet_buffer)
            parquet_buffer.seek(0)
            dataframes.append(pd.read_parquet(parquet_buffer))

        logger.info(f"Download all {file_extension} files from bucket {self._bucket_name} with path {path}")
        return pd.concat(dataframes, ignore_index=True)

    def find_keys(self, path: str) -> list[str]:
        client = connection_registry.get_item(self._connection_name)
        response = client.list_objects_v2(Bucket=self._bucket_name, Prefix=normalize_relative_path(path))

        object_keys = [object_metadata["Key"] for object_metadata in response.get("Contents", [])]
        logger.debug("Found datalake objects: bucket=%s path=%s objects=%s", self._bucket_name, path, len(object_keys))
        return object_keys

