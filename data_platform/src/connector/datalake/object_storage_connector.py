from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import boto3

from config.datalake import settings as datalake_settings


@contextmanager
def create_connection() -> Iterator[Any]:
    client = boto3.client(
        service_name="s3",
        endpoint_url=datalake_settings.endpoint,
        aws_access_key_id=datalake_settings.access_key,
        aws_secret_access_key=datalake_settings.secret_key,
    )

    try:
        yield client
    finally:
        client.close()
