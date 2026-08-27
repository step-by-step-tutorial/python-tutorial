import logging
from pathlib import Path

import boto3

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
            raise FileNotFoundError(
                f"No CSV files found in bucket '{self.bucket_name}' with prefix '{self.object_prefix}'."
            )

        source = max(objects, key=lambda item: item.get("LastModified"))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Downloading house dataset: bucket={self.bucket_name} key={source['Key']} output={output_path}")
        self._client.download_file(self.bucket_name, source["Key"], str(output_path))
        logger.info(f"House dataset downloaded: bytes={source.get('Size', 0)} output={output_path}")
        return output_path

    def get_object_keys(self) -> list[dict]:
        response = self._client.list_objects_v2(Bucket=self.bucket_name, Prefix=self.object_prefix)
        objects = [item for item in response.get("Contents", []) if item["Key"].lower().endswith(".csv")]
        logger.info(f"Found CSV objects: bucket={self.bucket_name} prefix={self.object_prefix} count={len(objects)}")
        return objects
