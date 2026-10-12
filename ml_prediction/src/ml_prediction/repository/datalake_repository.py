import logging
from io import BytesIO
from pathlib import Path
from typing import Any

import boto3
import pandas as pd

from ml_prediction.model.settings_model import DataLakeSettingsModel

logger = logging.getLogger(__name__)


class DataLakeRepository:
    def __init__(self, settings: DataLakeSettingsModel, client: Any = None) -> None:
        self._settings = settings
        self._client = client or boto3.client(
            "s3",
            endpoint_url=settings.endpoint,
            aws_access_key_id=settings.access_key,
            aws_secret_access_key=settings.secret_key,
        )

    def download_latest_partition(self, path: Path) -> Path:
        objects = self.find_parquet_objects()
        if not objects:
            raise ValueError(
                f"No Parquet files found: bucket={self._settings.bucket_name} prefix={self._settings.object_prefix}"
            )

        partition = self._latest_partition(objects)
        dataframe = pd.concat([self._read_parquet(item["Key"]) for item in partition], ignore_index=True)
        path.parent.mkdir(parents=True, exist_ok=True)
        dataframe.to_csv(path, index=False)
        logger.info("Downloaded dataset: bucket=%s prefix=%s files=%s rows=%s path=%s", self._settings.bucket_name,
                    self._settings.object_prefix, len(partition), len(dataframe), path)
        return path

    def find_parquet_objects(self) -> list[dict[str, Any]]:
        paginator = self._client.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=self._settings.bucket_name, Prefix=self._settings.object_prefix)
        return [
            item
            for page in pages
            for item in page.get("Contents", [])
            if item["Key"].lower().endswith(".parquet")
        ]

    def _read_parquet(self, key: str) -> pd.DataFrame:
        buffer = BytesIO()
        self._client.download_fileobj(self._settings.bucket_name, key, buffer)
        buffer.seek(0)
        return pd.read_parquet(buffer)

    @staticmethod
    def _latest_partition(objects: list[dict[str, Any]]) -> list[dict[str, Any]]:
        partitions: dict[str, list[dict[str, Any]]] = {}
        for item in objects:
            partitions.setdefault(item["Key"].rsplit("/", 1)[0], []).append(item)
        return max(partitions.values(), key=lambda items: max(item["LastModified"] for item in items))
