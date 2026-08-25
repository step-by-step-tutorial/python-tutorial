import boto3

from data_platform.config.keys import Key
from data_platform.config.main_settings import settings as main_settings


def create_sale_connection():
    return boto3.client(
        service_name="s3",
        endpoint_url=main_settings.data_lake[Key.SALE_DATA_LAKE].endpoint,
        aws_access_key_id=main_settings.data_lake[Key.SALE_DATA_LAKE].access_key,
        aws_secret_access_key=main_settings.data_lake[Key.SALE_DATA_LAKE].secret_key,
    )


def create_house_connection():
    return boto3.client(
        service_name="s3",
        endpoint_url=main_settings.data_lake[Key.HOUSE_DATA_LAKE].endpoint,
        aws_access_key_id=main_settings.data_lake[Key.HOUSE_DATA_LAKE].access_key,
        aws_secret_access_key=main_settings.data_lake[Key.HOUSE_DATA_LAKE].secret_key,
    )


def create_audit_connection():
    return boto3.client(
        service_name="s3",
        endpoint_url=main_settings.data_lake[Key.AUDIT_DATA_LAKE].endpoint,
        aws_access_key_id=main_settings.data_lake[Key.AUDIT_DATA_LAKE].access_key,
        aws_secret_access_key=main_settings.data_lake[Key.AUDIT_DATA_LAKE].secret_key,
    )


def create_online_shopping_connection():
    return boto3.client(
        service_name="s3",
        endpoint_url=main_settings.data_lake[Key.PLATFORM_DATA_LAKE].endpoint,
        aws_access_key_id=main_settings.data_lake[Key.PLATFORM_DATA_LAKE].access_key,
        aws_secret_access_key=main_settings.data_lake[Key.PLATFORM_DATA_LAKE].secret_key,
    )

