
import boto3

from data_platform.config.main_settings import settings as main_settings
from data_platform.keys import Key


def create_sale_connection():
    return boto3.client(
        service_name="s3",
        endpoint_url=main_settings.datalake[Key.SALE_DATALAKE].endpoint,
        aws_access_key_id=main_settings.datalake[Key.SALE_DATALAKE].access_key,
        aws_secret_access_key=main_settings.datalake[Key.SALE_DATALAKE].secret_key,
    )


def create_house_connection():
    return boto3.client(
        service_name="s3",
        endpoint_url=main_settings.datalake[Key.HOUSE_DATALAKE].endpoint,
        aws_access_key_id=main_settings.datalake[Key.HOUSE_DATALAKE].access_key,
        aws_secret_access_key=main_settings.datalake[Key.HOUSE_DATALAKE].secret_key,
    )


def create_audit_connection():
    return boto3.client(
        service_name="s3",
        endpoint_url=main_settings.datalake[Key.AUDIT_DATALAKE].endpoint,
        aws_access_key_id=main_settings.datalake[Key.AUDIT_DATALAKE].access_key,
        aws_secret_access_key=main_settings.datalake[Key.AUDIT_DATALAKE].secret_key,
    )
