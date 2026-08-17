from config.app import settings as app_settings
from config.audit import settings as audit_settings
from config.datalake import settings as datalake_settings
from config.datawarehouse import settings as datawarehouse_settings
from dataset.definition import (
    Audit,
    DataLakeEndpoint,
    DataWarehouseEndpoint,
    Dataframe,
    DatabaseEndpoint,
    Dataset,
    FileEndpoint,
    MessagingEndpoint,
)
from dataset.house.attribute import HOUSE_ATTRIBUTE as columns
from dataset.house.spark_schema import build_schema
from processor.inmemory.house_processor import InmemoryHouseProcessor
from processor.spark.house_processor import SparkHouseProcessor

HOUSE_DATASET = Dataset(
    name="house",
    dataframe=Dataframe(
        schema=build_schema(),
        required_columns=frozenset(
            {
                columns.area_raw,
                columns.room_raw,
                columns.parking_raw,
                columns.warehouse_raw,
                columns.elevator_raw,
                columns.address_raw,
                columns.price_raw,
                columns.price_usd_raw,
            }
        ),
    ),
    audit=Audit(topic=audit_settings.streaming_topic, archive_enabled=audit_settings.archive_enabled),
    sources={
        "file": FileEndpoint(
            name="file",
            file_name="house.csv",
            file_path=str(app_settings.root / app_settings.resources_dir / "house.csv"),
        ),
        "messaging": MessagingEndpoint(
            name="messaging",
            topic="house-events",
        ),
    },
    destinations={
        "datalake": DataLakeEndpoint(name="datalake", bucket_name=datalake_settings.bucket_name),
        "database": DatabaseEndpoint(
            name="database",
            table_name="house.house_stage",
            before_setup_sql_files=("database/house/truncate_stage.sql",),
            after_setup_sql_files=(),
        ),
        "datawarehouse": DataWarehouseEndpoint(
            name="datawarehouse",
            table_name="house_table",
            full_table_name=f"{datawarehouse_settings.database_name}.house_table",
            before_setup_sql_files={
                "truncate": "datawarehouse/house/truncate_datawarehouse.sql",
            },
            after_setup_sql_files={
                "average_price_by_address": "datawarehouse/house/select_average_price_by_address.sql",
                "average_price_per_square_meter_by_room": "datawarehouse/house/select_average_price_per_square_meter_by_room.sql",
            },
        ),
    },
    processor_factories={
        "inmemory": InmemoryHouseProcessor,
        "spark": SparkHouseProcessor,
    },
)
