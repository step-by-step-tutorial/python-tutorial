import logging
from io import BytesIO
from uuid import uuid4

import pandas as pd

from factory import datalake_connection_factory


def get_bucket_names(client) -> list[str]:
    response = client.list_buckets()
    return [bucket["Name"] for bucket in response.get("Buckets", [])]

logger = logging.getLogger(__name__)


def upload(df: pd.DataFrame, bucket_name: str, relative_path: str, file_extension: str = "parquet") -> str:
    parquet_buffer = BytesIO()
    df.to_parquet(parquet_buffer, index=False)
    parquet_buffer.seek(0)

    object_key = f"{relative_path.strip('/')}/part-{uuid4()}.{file_extension}"
    logger.info("Upload a %s file in bucket %s with path %s", file_extension, bucket_name, object_key)

    with datalake_connection_factory.create_connection() as client:
        if bucket_name not in get_bucket_names(client):
            client.create_bucket(Bucket=bucket_name)

        client.put_object(Bucket=bucket_name, Key=object_key, Body=parquet_buffer)

    return object_key


def download(bucket_name: str, relative_path: str, file_extension: str = "parquet") -> pd.DataFrame:
    logger.info("Download all %s files from bucket %s with path %s", file_extension, bucket_name, relative_path)
    dataframes = []

    with datalake_connection_factory.create_connection() as client:
        response = client.list_objects_v2(Bucket=bucket_name, Prefix=relative_path.strip("/"))

        for object_metadata in response.get("Contents", []):
            object_key = object_metadata["Key"]

            if not object_key.endswith(f".{file_extension}"):
                continue

            parquet_buffer = BytesIO()
            client.download_fileobj(bucket_name, object_key, parquet_buffer)
            parquet_buffer.seek(0)
            dataframes.append(pd.read_parquet(parquet_buffer))

    if not dataframes:
        raise FileNotFoundError(f"No {file_extension} files found under path: {relative_path}")

    return pd.concat(dataframes, ignore_index=True)
