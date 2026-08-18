from __future__ import annotations

import atexit
from typing import Any, Callable

import boto3

from config.settings import settings as main_settings

registry: dict[str, Any] = {}
factories: dict[str, Callable[[], Any]] = {}


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


factories["sale.datalake"] = create_sale_connection
factories["house.datalake"] = create_house_connection
factories["audit.datalake"] = create_audit_connection


def get_connection(name: str):
    if name not in registry:
        registry[name] = factories[name]()
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
