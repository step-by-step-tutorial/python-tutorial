from typing import Any

import boto3

from data_platform.model.settings_model import DataLakeSettingsModel


def create_datalake_client(settings: DataLakeSettingsModel) -> Any:
    return boto3.client(
        service_name="s3",
        endpoint_url=settings.endpoint,
        aws_access_key_id=settings.access_key,
        aws_secret_access_key=settings.secret_key,
    )
