import logging
from io import BytesIO
from pathlib import Path

import boto3
import pandas as pd

from ml_prediction.config.settings import get_settings
from ml_prediction.utils.data_validator_utils import require_not_blank
from ml_prediction.utils.datalake_utils import find_latest_partition

logger = logging.getLogger(__name__)


class DataLakeRepository:
    def __init__(self, dataset_name: str) -> None:
        settings = get_settings(dataset_name).data_lake
        self._settings = settings
        self.bucket_name = settings.bucket_name
        self.object_prefix = settings.object_prefix
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.endpoint,
            aws_access_key_id=settings.access_key,
            aws_secret_access_key=settings.secret_key,
        )

    def download_latest_csv(self, path: Path) -> Path:
        objects = self.get_object_keys()
        require_not_blank(
            obj=objects,
            error_message=f"No Parquet files found in bucket '{self.bucket_name}' with prefix '{self.object_prefix}'."
        )

        latest_partition = find_latest_partition(objects)
        path.parent.mkdir(parents=True, exist_ok=True)
        dataframes = []
        for source in latest_partition:
            parquet_buffer = BytesIO()
            self._client.download_fileobj(self.bucket_name, source["Key"], parquet_buffer)
            parquet_buffer.seek(0)
            dataframes.append(pd.read_parquet(parquet_buffer))

        pd.concat(dataframes, ignore_index=True).to_csv(path, index=False)
        logger.info(
            f"Enriched dataset downloaded: "
            f"bucket={self.bucket_name} "
            f"prefix={self.object_prefix} "
            f"files={len(latest_partition)} "
            f"output={path}"
        )
        return path

    def get_object_keys(self) -> list[dict]:
        response = self._client.list_objects_v2(Bucket=self.bucket_name, Prefix=self.object_prefix)
        objects = [item for item in response.get("Contents", []) if item["Key"].lower().endswith(".parquet")]
        logger.info(f"Found Parquet objects: bucket={self.bucket_name} prefix={self.object_prefix} count={len(objects)}")
        return objects
