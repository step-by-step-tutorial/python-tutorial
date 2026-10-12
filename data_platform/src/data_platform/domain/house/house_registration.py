from functools import partial

from data_platform.config.key import Key
from data_platform.config.settings import settings
from data_platform.connector.database_connector import create_database_engine
from data_platform.connector.datalake_connector import create_datalake_client
from data_platform.connector.kafka_connector import create_consumer, create_producer
from data_platform.connector.warehouse_connector import create_warehouse_client
from data_platform.domain.house.house_dataset import create_house_dataset
from data_platform.model.endpoint_model import (
    DataLakeEndpointModel, DatabaseEndpointModel, FileEndpointModel, MessagingEndpointModel, RestApiEndpointModel,
    WarehouseEndpointModel,
)
from data_platform.registry.connection_registry import connection_registry
from data_platform.registry.dataset_registry import dataset_registry
from data_platform.registry.endpoint_registry import endpoint_registry


def register_house() -> None:
    database = settings.database[Key.HOUSE_DATABASE]
    data_lake = settings.data_lake[Key.HOUSE_DATA_LAKE]
    warehouse = settings.warehouse[Key.HOUSE_WAREHOUSE]
    messaging = settings.messaging[Key.HOUSE_MESSAGING]

    connection_registry.register_lazy_item(Key.HOUSE_DATABASE, partial(create_database_engine, database))
    connection_registry.register_lazy_item(Key.HOUSE_DATA_LAKE, partial(create_datalake_client, data_lake))
    connection_registry.register_lazy_item(Key.HOUSE_WAREHOUSE, partial(create_warehouse_client, warehouse))
    connection_registry.register_lazy_item(Key.HOUSE_KAFKA_PRODUCER, partial(create_producer, messaging))
    connection_registry.register_lazy_item(Key.HOUSE_KAFKA_CONSUMER, partial(create_consumer, messaging))

    endpoints = (
        FileEndpointModel(
            name=Key.HOUSE_CSV_FILE,
            file_name="house.csv",
            file_path=str(settings.app.resource_path("house.csv")),
        ),
        RestApiEndpointModel(name=Key.HOUSE_REST_API, url=settings.data_simulator.dataset_download_url("house")),
        MessagingEndpointModel(
            name=Key.HOUSE_KAFKA_CONSUMER,
            connection_name=Key.HOUSE_KAFKA_CONSUMER,
            channel_name=messaging.channel_name,
            bootstrap_servers=messaging.bootstrap_servers,
            starting_offsets=messaging.starting_offsets,
        ),
        MessagingEndpointModel(
            name=Key.HOUSE_KAFKA_PRODUCER,
            connection_name=Key.HOUSE_KAFKA_PRODUCER,
            channel_name=messaging.channel_name,
            bootstrap_servers=messaging.bootstrap_servers,
        ),
        DataLakeEndpointModel(
            name=Key.HOUSE_DATA_LAKE,
            connection_name=Key.HOUSE_DATA_LAKE,
            bucket_name=data_lake.bucket_name,
            scheme=data_lake.scheme,
        ),
        DataLakeEndpointModel(
            name=Key.HOUSE_BACKUP_DATA_LAKE,
            connection_name=Key.HOUSE_DATA_LAKE,
            bucket_name=data_lake.backup_bucket_name,
            scheme=data_lake.scheme,
        ),
        DatabaseEndpointModel(
            name=Key.HOUSE_DATABASE,
            connection_name=Key.HOUSE_DATABASE,
            schema="house",
            stage_table_name="house_stage",
            create_sql_files={"create": "database/house/create_tables.sql"},
            truncate_sql_files={"truncate": "database/house/truncate_stage.sql"},
            query_sql_files={"select_all": "database/select_all.sql"},
        ),
        WarehouseEndpointModel(
            name=Key.HOUSE_WAREHOUSE,
            connection_name=Key.HOUSE_WAREHOUSE,
            schema=warehouse.database_name,
            table_name="house_table",
            create_sql_files={
                "create_database": "warehouse/house/create_database.sql",
                "create_table": "warehouse/house/create_table.sql",
            },
            truncate_sql_files={"truncate": "warehouse/house/truncate_warehouse.sql"},
            query_sql_files={
                "select_all": "warehouse/select_all.sql",
                "average_price_by_city": "warehouse/house/select_average_price_by_address.sql",
                "average_price_per_square_meter_by_property_type":
                    "warehouse/house/select_average_price_per_square_meter_by_room.sql",
            },
        ),
    )
    for endpoint in endpoints:
        endpoint_registry.register(endpoint.name, endpoint)

    dataset_registry.register("house", create_house_dataset)
