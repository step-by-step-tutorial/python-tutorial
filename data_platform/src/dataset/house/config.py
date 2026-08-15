from app_config import env_config as ec
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
from dataset.house import model as schema
from model.house_event import HouseEvent
from processor.inmemory.house_processor import InmemoryHouseProcessor
from processor.spark.house_processor import SparkHouseProcessor


def _schema():
    return schema.get_struct_type()


HOUSE_DATASET = Dataset(
    name="house",
    dataframe=Dataframe(
        schema_factory=_schema,
        required_columns=schema.required_columns,
    ),
    event=Event(
        key_column=schema.model.address_raw,
        converter=lambda row: HouseEvent.from_dict(row).to_dict(),
    ),
    audit=Audit(
        topic=ec.APP_STREAMING_AUDIT_TOPIC,
        archive_enabled=ec.APP_AUDIT_ARCHIVE_ENABLED,
    ),
    sources={
        "file": FileEndpoint(
            name="file",
            file_name="house.csv",
            file_path=str(ec.ROOT / ec.RESOURCES_DIR / "house.csv"),
        ),
        "messaging": MessagingEndpoint(
            name="messaging",
            topic="house-events",
            server=ec.APP_STREAMING_BOOTSTRAP_SERVERS,
            bootstrap_servers=ec.APP_STREAMING_BOOTSTRAP_SERVERS,
            checkpoint_path=f"{ec.APP_DATALAKE_SCHEME}://{ec.APP_DATALAKE_BUCKET_NAME}/checkpoints/house-events",
            starting_offsets=ec.APP_STREAMING_STARTING_OFFSETS,
        ),
    },
    destinations={
        "datalake": DataLakeEndpoint(name="datalake"),
        "database": DatabaseEndpoint(
            name="database",
            table_name="house.house_stage",
            before_load_sql_files=("database/house/truncate_stage.sql",),
            after_load_sql_files=(),
        ),
        "datawarehouse": DataWarehouseEndpoint(
            name="datawarehouse",
            table_name="house_table",
            full_table_name=f"{ec.APP_DATAWAREHOUSE_NAME}.house_table",
            preparing_sql_files={
                "truncate": "datawarehouse/house/truncate_datawarehouse.sql",
            },
            analysis_sql_files={
                "average_price_by_address": "datawarehouse/house/select_average_price_by_address.sql",
                "average_price_per_square_meter_by_room": "datawarehouse/house/select_average_price_per_square_meter_by_room.sql",
            },
        ),
    },
    processors={
        "inmemory": InmemoryHouseProcessor(),
        "spark": SparkHouseProcessor(),
    },
)
