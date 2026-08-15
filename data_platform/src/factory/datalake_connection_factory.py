from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import boto3

from app_config import env_config as ec


@contextmanager
def create_connection() -> Iterator[Any]:
    client = boto3.client(
        service_name="s3",
        endpoint_url=ec.APP_DATALAKE_ENDPOINT,
        aws_access_key_id=ec.APP_DATALAKE_ACCESS_KEY,
        aws_secret_access_key=ec.APP_DATALAKE_SECRET_KEY,
    )

    try:
        yield client
    finally:
        client.close()
