from dataclasses import dataclass
from typing import Mapping

from data_platform.config.app_settings import AppSettings, app
from data_platform.config.database_settings import DatabaseSettings, database
from data_platform.config.datalake_settings import DataLakeSettings, datalake
from data_platform.config.datawarehouse_settings import DataWarehouseSettings, datawarehouse
from data_platform.config.messaging_settings import MessagingSettings, messaging
from data_platform.config.spark_settings import SparkSettings, spark
from data_platform.config.test_data_settings import TestDataSettings, test_data

@dataclass(frozen=True)
class MainSettings:
    app: AppSettings
    database: Mapping[str, DatabaseSettings]
    datalake: Mapping[str, DataLakeSettings]
    datawarehouse: Mapping[str, DataWarehouseSettings]
    messaging: Mapping[str, MessagingSettings]
    test_data: TestDataSettings
    spark: SparkSettings
settings = MainSettings(
    app=app,
    database=database,
    datalake=datalake,
    datawarehouse=datawarehouse,
    messaging=messaging,
    test_data=test_data,
    spark=spark,
)
