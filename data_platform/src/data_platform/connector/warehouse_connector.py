from typing import Any

import clickhouse_connect

from data_platform.model.settings_model import WarehouseSettingsModel


def create_warehouse_client(settings: WarehouseSettingsModel) -> Any:
    return clickhouse_connect.get_client(
        host=settings.host,
        port=settings.port,
        database=settings.database_name,
        username=settings.user,
        password=settings.password,
    )
