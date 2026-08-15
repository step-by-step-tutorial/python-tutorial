from config.app import settings as app_settings
from config.audit import settings as audit_settings
from config.datalake import settings as datalake_settings
from config.datawarehouse import settings as datawarehouse_settings
from config.messaging import settings as messaging_settings
from dataset.definition import (
    Audit,
    DataLakeEndpoint,
    DataWarehouseEndpoint,
    Dataframe,
    DatabaseEndpoint,
    Dataset,
    Event,
    FileEndpoint,
    MessagingEndpoint,
)
from dataset.house.columns import house_columns as columns
from dataset.house.spark_schema import build_schema


def _schema():
    return build_schema()


def _inmemory_processor():
    from processor.inmemory.house_processor import InmemoryHouseProcessor

    return InmemoryHouseProcessor()


def _spark_processor():
    from processor.spark.house_processor import SparkHouseProcessor

    return SparkHouseProcessor()


HOUSE_DATASET = Dataset(
    name="house",
    dataframe=Dataframe(
        schema_factory=_schema,
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
    event=Event(
        key_column=columns.address_raw,
    ),
    audit=Audit(
        topic=audit_settings.streaming_topic,
        archive_enabled=audit_settings.archive_enabled,
    ),
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
            before_load_sql_files=("database/house/truncate_stage.sql",),
            after_load_sql_files=(),
        ),
        "datawarehouse": DataWarehouseEndpoint(
            name="datawarehouse",
            table_name="house_table",
            full_table_name=f"{datawarehouse_settings.database_name}.house_table",
            preparing_sql_files={
                "truncate": "datawarehouse/house/truncate_datawarehouse.sql",
            },
            analysis_sql_files={
                "average_price_by_address": "datawarehouse/house/select_average_price_by_address.sql",
                "average_price_per_square_meter_by_room": "datawarehouse/house/select_average_price_per_square_meter_by_room.sql",
            },
        ),
    },
    processor_factories={
        "inmemory": _inmemory_processor,
        "spark": _spark_processor,
    },
)
