from data_platform.config.main_settings import settings as main_settings
from data_platform.house.attribute import HOUSE_ATTRIBUTE as columns
from data_platform.house.inmemory_analyzer import InmemoryHouseAnalyzer
from data_platform.house.inmemory_transformer import InmemoryHouseTransformer
from data_platform.house.spark_analyzer import SparkHouseAnalyzer
from data_platform.house.spark_schema import build_schema
from data_platform.house.spark_transformer import SparkHouseTransformer
from data_platform.house.data_warehouse_analyzer import DataWarehouseHouseAnalyzer
from data_platform.keys import Key
from data_platform.model import (
    DataLakeEndpoint,
    DataWarehouseEndpoint,
    DataFrameDefinition,
    DatabaseEndpoint,
    Dataset,
    FileEndpoint,
    MessagingEndpoint,
)
from data_platform.registry.endpoint_registry import audit_endpoint, endpoint_registry
from data_platform.registry.dataset_registry import dataset_registry

HOUSE_DATASET = Dataset(
    name="house",
    dataframe=DataFrameDefinition(
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
    audit=endpoint_registry.get_item(audit_endpoint.name),
    endpoints={
        Key.HOUSE_FILE_CSV: FileEndpoint(
            name=Key.HOUSE_FILE_CSV,
            file_name="house.csv",
            file_path=str(main_settings.app.root / main_settings.app.resources_dir / "house.csv"),
        ),
        Key.HOUSE_KAFKA_LISTENER: MessagingEndpoint(
            name=Key.HOUSE_KAFKA_LISTENER,
            connection_name=Key.HOUSE_KAFKA_LISTENER,
            channel_name=main_settings.messaging[Key.HOUSE_KAFKA_LISTENER].channel_name,
            bootstrap_servers=main_settings.messaging[Key.HOUSE_KAFKA_LISTENER].bootstrap_servers,
            starting_offsets=main_settings.messaging[Key.HOUSE_KAFKA_LISTENER].starting_offsets,
        ),
        Key.HOUSE_KAFKA_PRODUCER: MessagingEndpoint(
            name=Key.HOUSE_KAFKA_PRODUCER,
            connection_name=Key.HOUSE_KAFKA_PRODUCER,
            channel_name=main_settings.messaging[Key.HOUSE_KAFKA_LISTENER].channel_name,
            bootstrap_servers=main_settings.messaging[Key.HOUSE_KAFKA_LISTENER].bootstrap_servers,
        ),
        Key.HOUSE_DATALAKE: DataLakeEndpoint(
            name=Key.HOUSE_DATALAKE,
            connection_name=Key.HOUSE_DATALAKE,
            bucket_name=main_settings.data_lake[Key.HOUSE_DATALAKE].bucket_name,
            scheme=main_settings.data_lake[Key.HOUSE_DATALAKE].scheme,
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
            schema=main_settings.data_warehouse[Key.HOUSE_DATAWAREHOUSE].database_name,
            table_name="house_table",
            full_table_name=f"{main_settings.data_warehouse[Key.HOUSE_DATAWAREHOUSE].database_name}.house_table",
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
    transformers={
        "inmemory": InmemoryHouseTransformer(),
        "spark": SparkHouseTransformer(),
    },
    analyzers={
        "inmemory": InmemoryHouseAnalyzer(),
        "spark": SparkHouseAnalyzer(),
        "datawarehouse": DataWarehouseHouseAnalyzer(),
    },
)


def register_house_dataset() -> None:
    if not dataset_registry.contains(HOUSE_DATASET.name):
        dataset_registry.register(HOUSE_DATASET.name, HOUSE_DATASET)
