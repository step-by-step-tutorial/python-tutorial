import logging
from io import BytesIO
from pathlib import Path

import boto3
import pandas as pd

from ml_prediction.config.settings import DataLakeSettings

logger = logging.getLogger(__name__)


class DataLakeRepository:
    def __init__(self, settings: DataLakeSettings) -> None:
        self._settings = settings
        self.bucket_name = settings.bucket_name
        self.object_prefix = settings.object_prefix
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.endpoint,
            aws_access_key_id=settings.access_key,
            aws_secret_access_key=settings.secret_key,
        )

    def download_latest_csv(self, output_path: Path) -> Path:
        objects = self.get_object_keys()
        if not objects:
            raise FileNotFoundError(f"No Parquet files found in bucket '{self.bucket_name}' with prefix '{self.object_prefix}'.")

        latest_partition = max(
            self._partition_objects(objects).items(),
            key=lambda item: max(source.get("LastModified") for source in item[1]),
        )[1]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        dataframes = []
        for source in latest_partition:
            parquet_buffer = BytesIO()
            self._client.download_fileobj(self.bucket_name, source["Key"], parquet_buffer)
            parquet_buffer.seek(0)
            dataframes.append(pd.read_parquet(parquet_buffer))

        pd.concat(dataframes, ignore_index=True).to_csv(output_path, index=False)
        logger.info(
            "Enriched dataset downloaded: bucket=%s prefix=%s files=%s output=%s",
            self.bucket_name,
            self.object_prefix,
            len(latest_partition),
            output_path,
        )
        return output_path

    def get_object_keys(self) -> list[dict]:
        response = self._client.list_objects_v2(Bucket=self.bucket_name, Prefix=self.object_prefix)
        objects = [item for item in response.get("Contents", []) if item["Key"].lower().endswith(".parquet")]
        logger.info(f"Found Parquet objects: bucket={self.bucket_name} prefix={self.object_prefix} count={len(objects)}")
        return objects

    @staticmethod
    def _partition_objects(objects: list[dict]) -> dict[str, list[dict]]:
        partitions: dict[str, list[dict]] = {}
        for item in objects:
            partition = item["Key"].rsplit("/", 1)[0]
            partitions.setdefault(partition, []).append(item)
        return partitions
