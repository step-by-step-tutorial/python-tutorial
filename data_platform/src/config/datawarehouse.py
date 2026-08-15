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

