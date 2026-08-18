from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DataWarehouseSettings:
    host: str
    port: int
    database_name: str
    user: str
    password: str
    jdbc_url: str


sale_settings = DataWarehouseSettings(
    host=os.getenv("APP_SALE_DATAWAREHOUSE_HOST", "localhost"),
    port=int(os.getenv("APP_SALE_DATAWAREHOUSE_PORT", "8123")),
    database_name=os.getenv("APP_SALE_DATAWAREHOUSE_NAME", "app_datawarehouse"),
    user=os.getenv("APP_SALE_DATAWAREHOUSE_USER", "admin"),
    password=os.getenv("APP_SALE_DATAWAREHOUSE_PASSWORD", "admin"),
    jdbc_url=os.getenv(
        "APP_SALE_DATAWAREHOUSE_JDBC_URL",
        "jdbc:clickhouse://"
        f"{os.getenv('APP_SALE_DATAWAREHOUSE_HOST', 'localhost')}:"
        f"{os.getenv('APP_SALE_DATAWAREHOUSE_PORT', '8123')}/"
        f"{os.getenv('APP_SALE_DATAWAREHOUSE_NAME', 'app_datawarehouse')}",
    ),
)
house_settings = DataWarehouseSettings(
    host=os.getenv("APP_HOUSE_DATAWAREHOUSE_HOST", "localhost"),
    port=int(os.getenv("APP_HOUSE_DATAWAREHOUSE_PORT", "8123")),
    database_name=os.getenv("APP_HOUSE_DATAWAREHOUSE_NAME", "app_datawarehouse"),
    user=os.getenv("APP_HOUSE_DATAWAREHOUSE_USER", "admin"),
    password=os.getenv("APP_HOUSE_DATAWAREHOUSE_PASSWORD", "admin"),
    jdbc_url=os.getenv(
        "APP_HOUSE_DATAWAREHOUSE_JDBC_URL",
        "jdbc:clickhouse://"
        f"{os.getenv('APP_HOUSE_DATAWAREHOUSE_HOST', 'localhost')}:"
        f"{os.getenv('APP_HOUSE_DATAWAREHOUSE_PORT', '8123')}/"
        f"{os.getenv('APP_HOUSE_DATAWAREHOUSE_NAME', 'app_datawarehouse')}",
    ),
)
audit_settings = DataWarehouseSettings(
    host=os.getenv("APP_AUDIT_DATAWAREHOUSE_HOST", "localhost"),
    port=int(os.getenv("APP_AUDIT_DATAWAREHOUSE_PORT", "8123")),
    database_name=os.getenv("APP_AUDIT_DATAWAREHOUSE_NAME", "app_datawarehouse"),
    user=os.getenv("APP_AUDIT_DATAWAREHOUSE_USER", "admin"),
    password=os.getenv("APP_AUDIT_DATAWAREHOUSE_PASSWORD", "admin"),
    jdbc_url=os.getenv(
        "APP_AUDIT_DATAWAREHOUSE_JDBC_URL",
        "jdbc:clickhouse://"
        f"{os.getenv('APP_AUDIT_DATAWAREHOUSE_HOST', 'localhost')}:"
        f"{os.getenv('APP_AUDIT_DATAWAREHOUSE_PORT', '8123')}/"
        f"{os.getenv('APP_AUDIT_DATAWAREHOUSE_NAME', 'app_datawarehouse')}",
    ),
)

settings = DataWarehouseSettings(
    host=os.getenv("APP_DATAWAREHOUSE_HOST", "localhost"),
    port=int(os.getenv("APP_DATAWAREHOUSE_PORT", "8123")),
    database_name=os.getenv("APP_DATAWAREHOUSE_NAME", "app_datawarehouse"),
    user=os.getenv("APP_DATAWAREHOUSE_USER", "admin"),
    password=os.getenv("APP_DATAWAREHOUSE_PASSWORD", "admin"),
    jdbc_url=os.getenv(
        "APP_DATAWAREHOUSE_JDBC_URL",
        "jdbc:clickhouse://"
        f"{os.getenv('APP_DATAWAREHOUSE_HOST', 'localhost')}:"
        f"{os.getenv('APP_DATAWAREHOUSE_PORT', '8123')}/"
        f"{os.getenv('APP_DATAWAREHOUSE_NAME', 'app_datawarehouse')}",
    ),
)
