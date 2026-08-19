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
    RestApiEndpoint,
)
from dataset.house.attribute import HOUSE_ATTRIBUTE as columns
from dataset.house.spark_schema import build_schema
from keys import Key
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
        database_connection_name=Key.AUDIT_DATABASE,
        messaging_connection_name=Key.AUDIT_KAFKA_PRODUCER,
        datalake_connection_name=Key.AUDIT_DATALAKE,
        schema="audit",
        create_sql_files={"create": "database/audit/create_tables.sql"},
        channel_name=main_settings.messaging[Key.AUDIT_KAFKA_PRODUCER].audit_channel_name,
        bucket_name=main_settings.datalake[Key.AUDIT_DATALAKE].audit_bucket_name,
        write_sql_files={"write": "database/audit/insert_event.sql"},
    ),
    endpoints={
        Key.HOUSE_FILE_CSV: FileEndpoint(
            name=Key.HOUSE_FILE_CSV,
            file_name="house.csv",
            file_path=str(main_settings.app.root / main_settings.app.resources_dir / "house.csv"),
        ),
        Key.HOUSE_REST: RestApiEndpoint(
            name=Key.HOUSE_REST,
            url=main_settings.rest[Key.HOUSE_REST].url,
            method=main_settings.rest[Key.HOUSE_REST].method,
        ),
        Key.HOUSE_KAFKA_LISTENER: MessagingEndpoint(
            name=Key.HOUSE_KAFKA_LISTENER,
            connection_name=Key.HOUSE_KAFKA_LISTENER,
            channel_name=main_settings.messaging[Key.HOUSE_KAFKA_LISTENER].channel_name,
            bootstrap_servers=main_settings.messaging[Key.HOUSE_KAFKA_LISTENER].bootstrap_servers,
            starting_offsets=main_settings.messaging[Key.HOUSE_KAFKA_LISTENER].starting_offsets,
        ),
        Key.HOUSE_DATALAKE: DataLakeEndpoint(
            name=Key.HOUSE_DATALAKE,
            connection_name=Key.HOUSE_DATALAKE,
            bucket_name=main_settings.datalake[Key.HOUSE_DATALAKE].bucket_name,
            scheme=main_settings.datalake[Key.HOUSE_DATALAKE].scheme,
        ),
        Key.HOUSE_DATABASE: DatabaseEndpoint(
            name=Key.HOUSE_DATABASE,
            connection_name=Key.HOUSE_DATABASE,
            schema="house",
            stage_table_name="house_stage",
            full_stage_table_name="house.house_stage",
            table_names=["house.house_stage"],
            create_sql_files={"create": "database/house/create_tables.sql"},
            truncate_sql_files={"truncate": "database/house/truncate_stage.sql"},
            write_sql_files={},
            query_sql_files={"select_all": "database/select_all.sql"},
        ),
        Key.HOUSE_DATAWAREHOUSE: DataWarehouseEndpoint(
            name=Key.HOUSE_DATAWAREHOUSE,
            connection_name=Key.HOUSE_DATAWAREHOUSE,
            schema=main_settings.datawarehouse[Key.HOUSE_DATAWAREHOUSE].database_name,
            table_name="house_table",
            full_table_name=f"{main_settings.datawarehouse[Key.HOUSE_DATAWAREHOUSE].database_name}.house_table",
            create_sql_files={
                "create_database": "datawarehouse/house/create_database.sql",
                "create_table": "datawarehouse/house/create_table.sql",
            },
            truncate_sql_files={
                "truncate": "datawarehouse/house/truncate_datawarehouse.sql",
            },
            write_sql_files={},
            query_sql_files={
                "select_all": "datawarehouse/select_all.sql",
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
