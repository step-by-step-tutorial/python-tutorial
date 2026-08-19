from __future__ import annotations

import boto3

from config.settings import settings as main_settings


def create_sale_connection():
    return boto3.client(
        service_name="s3",
        endpoint_url=main_settings.datalake["sale.datalake"].endpoint,
        aws_access_key_id=main_settings.datalake["sale.datalake"].access_key,
        aws_secret_access_key=main_settings.datalake["sale.datalake"].secret_key,
    )


def create_house_connection():
    return boto3.client(
        service_name="s3",
        endpoint_url=main_settings.datalake["house.datalake"].endpoint,
        aws_access_key_id=main_settings.datalake["house.datalake"].access_key,
        aws_secret_access_key=main_settings.datalake["house.datalake"].secret_key,
    )


def create_audit_connection():
    return boto3.client(
        service_name="s3",
        endpoint_url=main_settings.datalake["audit.datalake"].endpoint,
        aws_access_key_id=main_settings.datalake["audit.datalake"].access_key,
        aws_secret_access_key=main_settings.datalake["audit.datalake"].secret_key,
    )
