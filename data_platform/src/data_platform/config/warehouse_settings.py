import os
from dataclasses import dataclass
from types import MappingProxyType

from data_platform.config.keys import Key


@dataclass(frozen=True)
class WarehouseSettings:
    host: str
    port: int
    database_name: str
    user: str
    password: str
    jdbc_url: str


warehouse = MappingProxyType(
    {
        Key.PLATFORM_WAREHOUSE: WarehouseSettings(
            host=os.getenv("DATA_PLATFORM_WAREHOUSE_HOST", "localhost"),
            port=int(os.getenv("DATA_PLATFORM_WAREHOUSE_PORT", "8123")),
            database_name=os.getenv("DATA_PLATFORM_WAREHOUSE_NAME", "app_warehouse"),
            user=os.getenv("DATA_PLATFORM_WAREHOUSE_USER", "admin"),
            password=os.getenv("DATA_PLATFORM_WAREHOUSE_PASSWORD", "admin"),
            jdbc_url=os.getenv(
                "DATA_PLATFORM_WAREHOUSE_JDBC_URL",
                "jdbc:clickhouse://"
                f"{os.getenv('DATA_PLATFORM_WAREHOUSE_HOST', 'localhost')}:"
                f"{os.getenv('DATA_PLATFORM_WAREHOUSE_PORT', '8123')}/"
                f"{os.getenv('DATA_PLATFORM_WAREHOUSE_NAME', 'app_warehouse')}",
            ),
        ),
        Key.SALE_WAREHOUSE: WarehouseSettings(
            host=os.getenv("DATA_PLATFORM_SALE_WAREHOUSE_HOST", "localhost"),
            port=int(os.getenv("DATA_PLATFORM_SALE_WAREHOUSE_PORT", "8123")),
            database_name=os.getenv("DATA_PLATFORM_SALE_WAREHOUSE_NAME", "app_warehouse"),
            user=os.getenv("DATA_PLATFORM_SALE_WAREHOUSE_USER", "admin"),
            password=os.getenv("DATA_PLATFORM_SALE_WAREHOUSE_PASSWORD", "admin"),
            jdbc_url=os.getenv(
                "DATA_PLATFORM_SALE_WAREHOUSE_JDBC_URL",
                "jdbc:clickhouse://"
                f"{os.getenv('DATA_PLATFORM_SALE_WAREHOUSE_HOST', 'localhost')}:"
                f"{os.getenv('DATA_PLATFORM_SALE_WAREHOUSE_PORT', '8123')}/"
                f"{os.getenv('DATA_PLATFORM_SALE_WAREHOUSE_NAME', 'app_warehouse')}",
            ),
        ),
        Key.HOUSE_WAREHOUSE: WarehouseSettings(
            host=os.getenv("DATA_PLATFORM_HOUSE_WAREHOUSE_HOST", "localhost"),
            port=int(os.getenv("DATA_PLATFORM_HOUSE_WAREHOUSE_PORT", "8123")),
            database_name=os.getenv("DATA_PLATFORM_HOUSE_WAREHOUSE_NAME", "app_warehouse"),
            user=os.getenv("DATA_PLATFORM_HOUSE_WAREHOUSE_USER", "admin"),
            password=os.getenv("DATA_PLATFORM_HOUSE_WAREHOUSE_PASSWORD", "admin"),
            jdbc_url=os.getenv(
                "DATA_PLATFORM_HOUSE_WAREHOUSE_JDBC_URL",
                "jdbc:clickhouse://"
                f"{os.getenv('DATA_PLATFORM_HOUSE_WAREHOUSE_HOST', 'localhost')}:"
                f"{os.getenv('DATA_PLATFORM_HOUSE_WAREHOUSE_PORT', '8123')}/"
                f"{os.getenv('DATA_PLATFORM_HOUSE_WAREHOUSE_NAME', 'app_warehouse')}",
            ),
        ),
        Key.ONLINE_SHOPPING_WAREHOUSE: WarehouseSettings(
            host=os.getenv("DATA_PLATFORM_ONLINE_SHOPPING_WAREHOUSE_HOST", "localhost"),
            port=int(os.getenv("DATA_PLATFORM_ONLINE_SHOPPING_WAREHOUSE_PORT", "8123")),
            database_name=os.getenv("DATA_PLATFORM_ONLINE_SHOPPING_WAREHOUSE_NAME", "app_warehouse"),
            user=os.getenv("DATA_PLATFORM_ONLINE_SHOPPING_WAREHOUSE_USER", "admin"),
            password=os.getenv("DATA_PLATFORM_ONLINE_SHOPPING_WAREHOUSE_PASSWORD", "admin"),
            jdbc_url=os.getenv("DATA_PLATFORM_ONLINE_SHOPPING_WAREHOUSE_JDBC_URL",
                               "jdbc:clickhouse://localhost:8123/app_warehouse"),
        ),
        Key.AUDIT_WAREHOUSE: WarehouseSettings(
            host=os.getenv("DATA_PLATFORM_AUDIT_WAREHOUSE_HOST", "localhost"),
            port=int(os.getenv("DATA_PLATFORM_AUDIT_WAREHOUSE_PORT", "8123")),
            database_name=os.getenv("DATA_PLATFORM_AUDIT_WAREHOUSE_NAME", "app_warehouse"),
            user=os.getenv("DATA_PLATFORM_AUDIT_WAREHOUSE_USER", "admin"),
            password=os.getenv("DATA_PLATFORM_AUDIT_WAREHOUSE_PASSWORD", "admin"),
            jdbc_url=os.getenv(
                "DATA_PLATFORM_AUDIT_WAREHOUSE_JDBC_URL",
                "jdbc:clickhouse://"
                f"{os.getenv('DATA_PLATFORM_AUDIT_WAREHOUSE_HOST', 'localhost')}:"
                f"{os.getenv('DATA_PLATFORM_AUDIT_WAREHOUSE_PORT', '8123')}/"
                f"{os.getenv('DATA_PLATFORM_AUDIT_WAREHOUSE_NAME', 'app_warehouse')}",
            ),
        ),
    }
)

