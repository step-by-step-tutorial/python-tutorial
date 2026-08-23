import os
from dataclasses import dataclass
from types import MappingProxyType

from data_platform.keys import Key

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
        Key.DATA_PLATFORM_DATAWAREHOUSE: DataWarehouseSettings(
            host=os.getenv("DATA_PLATFORM_DATAWAREHOUSE_HOST", "localhost"),
            port=int(os.getenv("DATA_PLATFORM_DATAWAREHOUSE_PORT", "8123")),
            database_name=os.getenv("DATA_PLATFORM_DATAWAREHOUSE_NAME", "app_datawarehouse"),
            user=os.getenv("DATA_PLATFORM_DATAWAREHOUSE_USER", "admin"),
            password=os.getenv("DATA_PLATFORM_DATAWAREHOUSE_PASSWORD", "admin"),
            jdbc_url=os.getenv(
                "DATA_PLATFORM_DATAWAREHOUSE_JDBC_URL",
                "jdbc:clickhouse://"
                f"{os.getenv('DATA_PLATFORM_DATAWAREHOUSE_HOST', 'localhost')}:"
                f"{os.getenv('DATA_PLATFORM_DATAWAREHOUSE_PORT', '8123')}/"
                f"{os.getenv('DATA_PLATFORM_DATAWAREHOUSE_NAME', 'app_datawarehouse')}",
            ),
        ),
        Key.SALE_DATAWAREHOUSE: DataWarehouseSettings(
            host=os.getenv("DATA_PLATFORM_SALE_DATAWAREHOUSE_HOST", "localhost"),
            port=int(os.getenv("DATA_PLATFORM_SALE_DATAWAREHOUSE_PORT", "8123")),
            database_name=os.getenv("DATA_PLATFORM_SALE_DATAWAREHOUSE_NAME", "app_datawarehouse"),
            user=os.getenv("DATA_PLATFORM_SALE_DATAWAREHOUSE_USER", "admin"),
            password=os.getenv("DATA_PLATFORM_SALE_DATAWAREHOUSE_PASSWORD", "admin"),
            jdbc_url=os.getenv(
                "DATA_PLATFORM_SALE_DATAWAREHOUSE_JDBC_URL",
                "jdbc:clickhouse://"
                f"{os.getenv('DATA_PLATFORM_SALE_DATAWAREHOUSE_HOST', 'localhost')}:"
                f"{os.getenv('DATA_PLATFORM_SALE_DATAWAREHOUSE_PORT', '8123')}/"
                f"{os.getenv('DATA_PLATFORM_SALE_DATAWAREHOUSE_NAME', 'app_datawarehouse')}",
            ),
        ),
        Key.HOUSE_DATAWAREHOUSE: DataWarehouseSettings(
            host=os.getenv("DATA_PLATFORM_HOUSE_DATAWAREHOUSE_HOST", "localhost"),
            port=int(os.getenv("DATA_PLATFORM_HOUSE_DATAWAREHOUSE_PORT", "8123")),
            database_name=os.getenv("DATA_PLATFORM_HOUSE_DATAWAREHOUSE_NAME", "app_datawarehouse"),
            user=os.getenv("DATA_PLATFORM_HOUSE_DATAWAREHOUSE_USER", "admin"),
            password=os.getenv("DATA_PLATFORM_HOUSE_DATAWAREHOUSE_PASSWORD", "admin"),
            jdbc_url=os.getenv(
                "DATA_PLATFORM_HOUSE_DATAWAREHOUSE_JDBC_URL",
                "jdbc:clickhouse://"
                f"{os.getenv('DATA_PLATFORM_HOUSE_DATAWAREHOUSE_HOST', 'localhost')}:"
                f"{os.getenv('DATA_PLATFORM_HOUSE_DATAWAREHOUSE_PORT', '8123')}/"
                f"{os.getenv('DATA_PLATFORM_HOUSE_DATAWAREHOUSE_NAME', 'app_datawarehouse')}",
            ),
        ),
        Key.AUDIT_DATAWAREHOUSE: DataWarehouseSettings(
            host=os.getenv("DATA_PLATFORM_AUDIT_DATAWAREHOUSE_HOST", "localhost"),
            port=int(os.getenv("DATA_PLATFORM_AUDIT_DATAWAREHOUSE_PORT", "8123")),
            database_name=os.getenv("DATA_PLATFORM_AUDIT_DATAWAREHOUSE_NAME", "app_datawarehouse"),
            user=os.getenv("DATA_PLATFORM_AUDIT_DATAWAREHOUSE_USER", "admin"),
            password=os.getenv("DATA_PLATFORM_AUDIT_DATAWAREHOUSE_PASSWORD", "admin"),
            jdbc_url=os.getenv(
                "DATA_PLATFORM_AUDIT_DATAWAREHOUSE_JDBC_URL",
                "jdbc:clickhouse://"
                f"{os.getenv('DATA_PLATFORM_AUDIT_DATAWAREHOUSE_HOST', 'localhost')}:"
                f"{os.getenv('DATA_PLATFORM_AUDIT_DATAWAREHOUSE_PORT', '8123')}/"
                f"{os.getenv('DATA_PLATFORM_AUDIT_DATAWAREHOUSE_NAME', 'app_datawarehouse')}",
            ),
        ),
    }
)
