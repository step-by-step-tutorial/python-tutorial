from __future__ import annotations

import atexit
from typing import Any

import boto3

from config.datalake import audit_settings, house_settings, sale_settings

registry: dict[str, Any] = {}


def create_sale_connection():
    return boto3.client(
        service_name="s3",
        endpoint_url=sale_settings.endpoint,
        aws_access_key_id=sale_settings.access_key,
        aws_secret_access_key=sale_settings.secret_key,
    )


def create_house_connection():
    return boto3.client(
        service_name="s3",
        endpoint_url=house_settings.endpoint,
        aws_access_key_id=house_settings.access_key,
        aws_secret_access_key=house_settings.secret_key,
    )


def create_audit_connection():
    return boto3.client(
        service_name="s3",
        endpoint_url=audit_settings.endpoint,
        aws_access_key_id=audit_settings.access_key,
        aws_secret_access_key=audit_settings.secret_key,
    )


registry["sale.datalake"] = create_sale_connection()
registry["house.datalake"] = create_house_connection()
registry["audit.datalake"] = create_audit_connection()


def get_connection(name: str):
    return registry[name]


def close_connection(name: str) -> None:
    connection = registry.pop(name, None)
    if connection is None:
        return

    if hasattr(connection, "close") and callable(connection.close):
        connection.close()


def close_all_connections() -> None:
    for name in list(registry):
        close_connection(name)


atexit.register(close_all_connections)
