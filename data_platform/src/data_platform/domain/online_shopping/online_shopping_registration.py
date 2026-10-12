from functools import partial

from data_platform.config.key import Key
from data_platform.config.settings import settings
from data_platform.connector.database_connector import create_database_engine
from data_platform.connector.datalake_connector import create_datalake_client
from data_platform.connector.warehouse_connector import create_warehouse_client
from data_platform.domain.online_shopping.online_shopping_dataset import create_online_shopping_dataset
from data_platform.model.endpoint_model import (
    DataLakeEndpointModel, DatabaseEndpointModel, MessagingEndpointModel, RestApiEndpointModel, WarehouseEndpointModel,
)
from data_platform.registry.connection_registry import connection_registry
from data_platform.registry.dataset_registry import dataset_registry
from data_platform.registry.endpoint_registry import endpoint_registry


def register_online_shopping() -> None:
    database = settings.database[Key.ONLINE_SHOPPING_DATABASE]
    data_lake = settings.data_lake[Key.ONLINE_SHOPPING_DATA_LAKE]
    warehouse = settings.warehouse[Key.ONLINE_SHOPPING_WAREHOUSE]
    messaging = settings.messaging[Key.ONLINE_SHOPPING_MESSAGING]

    connection_registry.register_lazy_item(Key.ONLINE_SHOPPING_DATABASE, partial(create_database_engine, database))
    connection_registry.register_lazy_item(Key.ONLINE_SHOPPING_DATA_LAKE, partial(create_datalake_client, data_lake))
    connection_registry.register_lazy_item(Key.ONLINE_SHOPPING_WAREHOUSE, partial(create_warehouse_client, warehouse))

    endpoints = (
        RestApiEndpointModel(
            name=Key.ONLINE_SHOPPING_REST_API,
            url=settings.data_simulator.dataset_download_url("online_shopping"),
        ),
        MessagingEndpointModel(
            name=Key.ONLINE_SHOPPING_KAFKA_CONSUMER,
            connection_name=Key.ONLINE_SHOPPING_KAFKA_CONSUMER,
            channel_name=messaging.channel_name,
            bootstrap_servers=messaging.bootstrap_servers,
            starting_offsets=messaging.starting_offsets,
        ),
        DataLakeEndpointModel(
            name=Key.ONLINE_SHOPPING_DATA_LAKE,
            connection_name=Key.ONLINE_SHOPPING_DATA_LAKE,
            bucket_name=data_lake.bucket_name,
            scheme=data_lake.scheme,
        ),
        DataLakeEndpointModel(
            name=Key.ONLINE_SHOPPING_BACKUP_DATA_LAKE,
            connection_name=Key.ONLINE_SHOPPING_DATA_LAKE,
            bucket_name=data_lake.backup_bucket_name,
            scheme=data_lake.scheme,
        ),
        DatabaseEndpointModel(
            name=Key.ONLINE_SHOPPING_DATABASE,
            connection_name=Key.ONLINE_SHOPPING_DATABASE,
            schema="online_shopping",
            stage_table_name="online_shopping_stage",
            create_sql_files={"create": "database/online_shopping/create_tables.sql"},
            truncate_sql_files={"truncate": "database/online_shopping/truncate_stage.sql"},
            query_sql_files={"select_all": "database/select_all.sql"},
        ),
        WarehouseEndpointModel(
            name=Key.ONLINE_SHOPPING_WAREHOUSE,
            connection_name=Key.ONLINE_SHOPPING_WAREHOUSE,
            schema=warehouse.database_name,
            table_name="online_shopping_table",
            create_sql_files={
                "create_database": "warehouse/online_shopping/create_database.sql",
                "create_table": "warehouse/online_shopping/create_table.sql",
            },
            truncate_sql_files={"truncate": "warehouse/online_shopping/truncate_warehouse.sql"},
            query_sql_files={
                "select_all": "warehouse/select_all.sql",
                "revenue_by_country": "warehouse/online_shopping/select_revenue_by_country.sql",
            },
        ),
    )
    for endpoint in endpoints:
        endpoint_registry.register(endpoint.name, endpoint)

    dataset_registry.register("online_shopping", create_online_shopping_dataset)
