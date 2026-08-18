from config.settings import settings as main_settings
from dataset.definition import (
    AuditEndpoint,
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
    audit=AuditEndpoint(
        database_connection_name="audit.database",
        messaging_connection_name="audit.kafka.producer",
        datalake_connection_name="audit.datalake",
        schema="audit",
        create_sql_files={"create": "database/audit/create_tables.sql"},
        channel_name=main_settings.messaging["audit"].audit_channel_name,
        bucket_name=main_settings.datalake["audit.datalake"].audit_bucket_name,
        write_sql_files={"write": "database/audit/insert_event.sql"},
    ),
    endpoints={
        "house.file.csv": FileEndpoint(
            name="file",
            file_name="house.csv",
            file_path=str(main_settings.app.root / main_settings.app.resources_dir / "house.csv"),
        ),
        "house.kafka.listener": MessagingEndpoint(
            name="messaging",
            connection_name="house.kafka.listener",
            channel_name=main_settings.messaging["house"].channel_name,
            bootstrap_servers=main_settings.messaging["house"].bootstrap_servers,
            starting_offsets=main_settings.messaging["house"].starting_offsets,
        ),
        "house.datalake": DataLakeEndpoint(
            name="datalake",
            connection_name="house.datalake",
            bucket_name=main_settings.datalake["house.datalake"].bucket_name,
            scheme=main_settings.datalake["house.datalake"].scheme,
        ),
        "house.database": DatabaseEndpoint(
            name="database",
            connection_name="house.database",
            schema="house",
            stage_table_name="house_stage",
            full_stage_table_name="house.house_stage",
            table_names=["house.house_stage"],
            create_sql_files={"create": "database/house/create_tables.sql"},
            truncate_sql_files={"truncate": "database/house/truncate_stage.sql"},
            write_sql_files={},
            query_sql_files={},
        ),
        "house.datawarehouse": DataWarehouseEndpoint(
            name="datawarehouse",
            connection_name="house.datawarehouse",
            schema=main_settings.datawarehouse["house.datawarehouse"].database_name,
            table_name="house_table",
            full_table_name=f"{main_settings.datawarehouse['house.datawarehouse'].database_name}.house_table",
            create_sql_files={
                "create_database": "datawarehouse/house/create_database.sql",
                "create_table": "datawarehouse/house/create_table.sql",
            },
            truncate_sql_files={
                "truncate": "datawarehouse/house/truncate_datawarehouse.sql",
            },
            write_sql_files={},
            query_sql_files={
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
