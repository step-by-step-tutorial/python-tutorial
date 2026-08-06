from io import BytesIO
from uuid import uuid4

import pandas as pd

from factory import datalake_connection_factory
from service.datalake import datalake_sale_service


def upload_parquet(dataframe: pd.DataFrame, bucket_name: str, path: str) -> str:
    parquet_buffer = BytesIO()
    dataframe.to_parquet(parquet_buffer, index=False)
    parquet_buffer.seek(0)

    object_key = f"{path.strip('/')}/part-{uuid4()}.parquet"

    with datalake_connection_factory.create_connection() as client:
        if bucket_name not in datalake_sale_service.get_bucket_names(client):
            client.create_bucket(Bucket=bucket_name)

        client.put_object(Bucket=bucket_name, Key=object_key, Body=parquet_buffer)

    return object_key


def download_parquet(bucket_name: str, path: str) -> pd.DataFrame:
    dataframes = []

    with datalake_connection_factory.create_connection() as client:
        response = client.list_objects_v2(Bucket=bucket_name, Prefix=path.strip("/"))

        for object_metadata in response.get("Contents", []):
            object_key = object_metadata["Key"]

            if not object_key.endswith(".parquet"):
                continue

            parquet_buffer = BytesIO()
            client.download_fileobj(bucket_name, object_key, parquet_buffer)
            parquet_buffer.seek(0)
            dataframes.append(pd.read_parquet(parquet_buffer))

    if not dataframes:
        raise FileNotFoundError(f"No Parquet files found under path: {path}")

    return pd.concat(dataframes, ignore_index=True)
