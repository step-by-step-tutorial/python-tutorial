import os
from dataclasses import dataclass
from types import MappingProxyType

from data_platform.config.keys import Key


@dataclass(frozen=True)
class DataWarehouseSettings:
    host: str
    port: int
    database_name: str
    user: str
    password: str
    jdbc_url: str


data_warehouse = MappingProxyType(
    {
        Key.PLATFORM_DATA_WAREHOUSE: DataWarehouseSettings(
            host=os.getenv("PLATFORM_DATA_WAREHOUSE_HOST", "localhost"),
            port=int(os.getenv("PLATFORM_DATA_WAREHOUSE_PORT", "8123")),
            database_name=os.getenv("PLATFORM_DATA_WAREHOUSE_NAME", "app_datawarehouse"),
            user=os.getenv("PLATFORM_DATA_WAREHOUSE_USER", "admin"),
            password=os.getenv("PLATFORM_DATA_WAREHOUSE_PASSWORD", "admin"),
            jdbc_url=os.getenv(
                "PLATFORM_DATA_WAREHOUSE_JDBC_URL",
                "jdbc:clickhouse://"
                f"{os.getenv('PLATFORM_DATA_WAREHOUSE_HOST', 'localhost')}:"
                f"{os.getenv('PLATFORM_DATA_WAREHOUSE_PORT', '8123')}/"
                f"{os.getenv('PLATFORM_DATA_WAREHOUSE_NAME', 'app_datawarehouse')}",
            ),
        ),
        Key.SALE_DATA_WAREHOUSE: DataWarehouseSettings(
            host=os.getenv("DATA_PLATFORM_SALE_DATA_WAREHOUSE_HOST", "localhost"),
            port=int(os.getenv("DATA_PLATFORM_SALE_DATA_WAREHOUSE_PORT", "8123")),
            database_name=os.getenv("DATA_PLATFORM_SALE_DATA_WAREHOUSE_NAME", "app_datawarehouse"),
            user=os.getenv("DATA_PLATFORM_SALE_DATA_WAREHOUSE_USER", "admin"),
            password=os.getenv("DATA_PLATFORM_SALE_DATA_WAREHOUSE_PASSWORD", "admin"),
            jdbc_url=os.getenv(
                "DATA_PLATFORM_SALE_DATA_WAREHOUSE_JDBC_URL",
                "jdbc:clickhouse://"
                f"{os.getenv('DATA_PLATFORM_SALE_DATA_WAREHOUSE_HOST', 'localhost')}:"
                f"{os.getenv('DATA_PLATFORM_SALE_DATA_WAREHOUSE_PORT', '8123')}/"
                f"{os.getenv('DATA_PLATFORM_SALE_DATA_WAREHOUSE_NAME', 'app_datawarehouse')}",
            ),
        ),
        Key.HOUSE_DATA_WAREHOUSE: DataWarehouseSettings(
            host=os.getenv("DATA_PLATFORM_HOUSE_DATA_WAREHOUSE_HOST", "localhost"),
            port=int(os.getenv("DATA_PLATFORM_HOUSE_DATA_WAREHOUSE_PORT", "8123")),
            database_name=os.getenv("DATA_PLATFORM_HOUSE_DATA_WAREHOUSE_NAME", "app_datawarehouse"),
            user=os.getenv("DATA_PLATFORM_HOUSE_DATA_WAREHOUSE_USER", "admin"),
            password=os.getenv("DATA_PLATFORM_HOUSE_DATA_WAREHOUSE_PASSWORD", "admin"),
            jdbc_url=os.getenv(
                "DATA_PLATFORM_HOUSE_DATA_WAREHOUSE_JDBC_URL",
                "jdbc:clickhouse://"
                f"{os.getenv('DATA_PLATFORM_HOUSE_DATA_WAREHOUSE_HOST', 'localhost')}:"
                f"{os.getenv('DATA_PLATFORM_HOUSE_DATA_WAREHOUSE_PORT', '8123')}/"
                f"{os.getenv('DATA_PLATFORM_HOUSE_DATA_WAREHOUSE_NAME', 'app_datawarehouse')}",
            ),
        ),
        Key.AUDIT_DATA_WAREHOUSE: DataWarehouseSettings(
            host=os.getenv("DATA_PLATFORM_AUDIT_DATA_WAREHOUSE_HOST", "localhost"),
            port=int(os.getenv("DATA_PLATFORM_AUDIT_DATA_WAREHOUSE_PORT", "8123")),
            database_name=os.getenv("DATA_PLATFORM_AUDIT_DATA_WAREHOUSE_NAME", "app_datawarehouse"),
            user=os.getenv("DATA_PLATFORM_AUDIT_DATA_WAREHOUSE_USER", "admin"),
            password=os.getenv("DATA_PLATFORM_AUDIT_DATA_WAREHOUSE_PASSWORD", "admin"),
            jdbc_url=os.getenv(
                "DATA_PLATFORM_AUDIT_DATA_WAREHOUSE_JDBC_URL",
                "jdbc:clickhouse://"
                f"{os.getenv('DATA_PLATFORM_AUDIT_DATA_WAREHOUSE_HOST', 'localhost')}:"
                f"{os.getenv('DATA_PLATFORM_AUDIT_DATA_WAREHOUSE_PORT', '8123')}/"
                f"{os.getenv('DATA_PLATFORM_AUDIT_DATA_WAREHOUSE_NAME', 'app_datawarehouse')}",
            ),
        ),
    }
)
