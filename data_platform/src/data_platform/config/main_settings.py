from dataclasses import dataclass
from typing import Mapping

from data_platform.config.api_settings import ApiSettings, api
from data_platform.config.app_settings import AppSettings, app
from data_platform.config.data_lake_settings import DataLakeSettings, data_lake
from data_platform.config.warehouse_settings import WarehouseSettings, warehouse
from data_platform.config.database_settings import DatabaseSettings, database
from data_platform.config.messaging_settings import MessagingSettings, messaging
from data_platform.config.spark_settings import SparkSettings, spark


@dataclass(frozen=True)
class MainSettings:
    app: AppSettings
    api: Mapping[str, ApiSettings]
    database: Mapping[str, DatabaseSettings]
    data_lake: Mapping[str, DataLakeSettings]
    warehouse: Mapping[str, WarehouseSettings]
    messaging: Mapping[str, MessagingSettings]
    spark: SparkSettings


settings = MainSettings(
    app=app,
    api=api,
    database=database,
    data_lake=data_lake,
    warehouse=warehouse,
    messaging=messaging,
    spark=spark,
)

