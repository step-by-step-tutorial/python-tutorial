from dataclasses import dataclass
from typing import Mapping

from data_platform.config.app_settings import AppSettings, app
from data_platform.config.database_settings import DatabaseSettings, database
from data_platform.config.data_lake_settings import DataLakeSettings, data_lake
from data_platform.config.data_warehouse_settings import DataWarehouseSettings, data_warehouse
from data_platform.config.messaging_settings import MessagingSettings, messaging
from data_platform.config.spark_settings import SparkSettings, spark
from data_platform.config.test_data_settings import TestDataSettings, test_data

@dataclass(frozen=True)
class MainSettings:
    app: AppSettings
    database: Mapping[str, DatabaseSettings]
    data_lake: Mapping[str, DataLakeSettings]
    data_warehouse: Mapping[str, DataWarehouseSettings]
    messaging: Mapping[str, MessagingSettings]
    test_data: TestDataSettings
    spark: SparkSettings
settings = MainSettings(
    app=app,
    database=database,
    data_lake=data_lake,
    data_warehouse=data_warehouse,
    messaging=messaging,
    test_data=test_data,
    spark=spark,
)
