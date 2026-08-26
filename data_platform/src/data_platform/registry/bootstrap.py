import data_platform.connector.database_connections
import data_platform.connector.datalake_connections
import data_platform.connector.kafka_connections
import data_platform.connector.warehouse_connections
from data_platform.config.keys import Key
from data_platform.config.main_settings import settings as main_settings
from data_platform.model.endpoints import (
    AuditEndpoint, DataLakeEndpoint, DatabaseEndpoint, FileEndpoint,
    MessagingEndpoint, RestApiEndpoint, WarehouseEndpoint,
)
from data_platform.registry.connection_registry import connection_registry
from data_platform.registry.dataset_registry import dataset_registry
from data_platform.registry.endpoint_registry import endpoint_registry
from data_platform.util.path_utils import generate_dataset_download_url, generate_project_path


def initialize_registries() -> None:
    connection_registry.clear()
    connection_registry.register_lazy_item(Key.HOUSE_DATABASE,
                                           data_platform.connector.database_connections.create_house_connection)
    connection_registry.register_lazy_item(Key.ONLINE_SHOPPING_DATABASE,
                                           data_platform.connector.database_connections.create_online_shopping_connection)
    connection_registry.register_lazy_item(Key.AUDIT_DATABASE,
                                           data_platform.connector.database_connections.create_audit_connection)
    connection_registry.register_lazy_item(Key.HOUSE_DATA_LAKE,
                                           data_platform.connector.datalake_connections.create_house_connection)
    connection_registry.register_lazy_item(Key.AUDIT_DATA_LAKE,
                                           data_platform.connector.datalake_connections.create_audit_connection)
    connection_registry.register_lazy_item(Key.ONLINE_SHOPPING_DATA_LAKE,
                                           data_platform.connector.datalake_connections.create_online_shopping_connection)
    connection_registry.register_lazy_item(Key.HOUSE_WAREHOUSE,
                                           data_platform.connector.warehouse_connections.create_house_connection)
    connection_registry.register_lazy_item(Key.ONLINE_SHOPPING_WAREHOUSE,
                                           data_platform.connector.warehouse_connections.create_online_shopping_connection)
    connection_registry.register_lazy_item(Key.AUDIT_WAREHOUSE,
                                           data_platform.connector.warehouse_connections.create_audit_connection)
    connection_registry.register_lazy_item(Key.HOUSE_KAFKA_PRODUCER,
                                           data_platform.connector.kafka_connections.create_house_publisher_connection)
    connection_registry.register_lazy_item(Key.AUDIT_KAFKA_PRODUCER,
                                           data_platform.connector.kafka_connections.create_audit_publisher_connection)
    connection_registry.register_lazy_item(Key.HOUSE_KAFKA_CONSUMER,
                                           data_platform.connector.kafka_connections.create_house_listener_connection)
    connection_registry.register_lazy_item(Key.AUDIT_KAFKA_CONSUMER,
                                           data_platform.connector.kafka_connections.create_audit_listener_connection)
    endpoint_registry.clear()
    endpoint_registry.register(
        "audit",
        AuditEndpoint(
            database_connection_name=Key.AUDIT_DATABASE,
            messaging_connection_name=Key.AUDIT_KAFKA_PRODUCER,
            datalake_connection_name=Key.AUDIT_DATA_LAKE,
            schema="audit",
            create_sql_files={"create": "database/audit/create_tables.sql"},
            channel_name=main_settings.messaging[Key.AUDIT_KAFKA_PRODUCER].audit_channel_name,
            bucket_name=main_settings.data_lake[Key.AUDIT_DATA_LAKE].audit_bucket_name,
            write_sql_files={"write": "database/audit/insert_event.sql"},
        ),
    )
    endpoint_registry.register(
        Key.HOUSE_CSV_FILE,
        FileEndpoint(
            name=Key.HOUSE_CSV_FILE,
            file_name="house.csv",
            file_path=str(generate_project_path(
                main_settings.app.root,
                main_settings.app.resources_dir,
                "house.csv",
            )),
        ))
    endpoint_registry.register(
        Key.HOUSE_REST_API,
        RestApiEndpoint(
            name=Key.HOUSE_REST_API,
            url=generate_dataset_download_url(main_settings.api["data_simulator"].url, "house"),
        ))
    endpoint_registry.register(
        Key.HOUSE_KAFKA_CONSUMER,
        MessagingEndpoint(
            name=Key.HOUSE_KAFKA_CONSUMER,
            connection_name=Key.HOUSE_KAFKA_CONSUMER,
            channel_name=main_settings.messaging[Key.HOUSE_KAFKA_CONSUMER].channel_name,
            bootstrap_servers=main_settings.messaging[Key.HOUSE_KAFKA_CONSUMER].bootstrap_servers,
            starting_offsets=main_settings.messaging[Key.HOUSE_KAFKA_CONSUMER].starting_offsets,
        ))
    endpoint_registry.register(
        Key.HOUSE_KAFKA_PRODUCER,
        MessagingEndpoint(
            name=Key.HOUSE_KAFKA_PRODUCER,
            connection_name=Key.HOUSE_KAFKA_PRODUCER,
            channel_name=main_settings.messaging[Key.HOUSE_KAFKA_CONSUMER].channel_name,
            bootstrap_servers=main_settings.messaging[Key.HOUSE_KAFKA_PRODUCER].bootstrap_servers,
        ))
    endpoint_registry.register(
        Key.HOUSE_DATA_LAKE,
        DataLakeEndpoint(
            name=Key.HOUSE_DATA_LAKE,
            connection_name=Key.HOUSE_DATA_LAKE,
            bucket_name=main_settings.data_lake[Key.HOUSE_DATA_LAKE].bucket_name,
            scheme=main_settings.data_lake[Key.HOUSE_DATA_LAKE].scheme,
        ))
    endpoint_registry.register(
        Key.HOUSE_BACKUP_DATA_LAKE,
        DataLakeEndpoint(
            name=Key.HOUSE_BACKUP_DATA_LAKE,
            connection_name=Key.HOUSE_DATA_LAKE,
            bucket_name=main_settings.data_lake[Key.HOUSE_BACKUP_DATA_LAKE].bucket_name,
            scheme=main_settings.data_lake[Key.HOUSE_BACKUP_DATA_LAKE].scheme,
        ))
    endpoint_registry.register(
        Key.HOUSE_DATABASE,
        DatabaseEndpoint(
            name=Key.HOUSE_DATABASE,
            connection_name=Key.HOUSE_DATABASE,
            schema="house",
            stage_table_name="house_stage",
            full_stage_table_name="house.house_stage",
            table_names=["house.house_stage"],
            create_sql_files={"create": "database/house/create_tables.sql"},
            truncate_sql_files={"truncate": "database/house/truncate_stage.sql"},
            query_sql_files={"select_all": "database/select_all.sql"},
        ))
    endpoint_registry.register(
        Key.HOUSE_WAREHOUSE,
        WarehouseEndpoint(
            name=Key.HOUSE_WAREHOUSE,
            connection_name=Key.HOUSE_WAREHOUSE,
            schema=main_settings.warehouse[Key.HOUSE_WAREHOUSE].database_name,
            table_name="house_table",
            full_table_name=f"{main_settings.warehouse[Key.HOUSE_WAREHOUSE].database_name}.house_table",
            create_sql_files={
                "create_database": "warehouse/house/create_database.sql",
                "create_table": "warehouse/house/create_table.sql",
            },
            truncate_sql_files={
                "truncate": "warehouse/house/truncate_warehouse.sql"
            },
            query_sql_files={
                "select_all": "warehouse/select_all.sql",
                "average_price_by_city": "warehouse/house/select_average_price_by_address.sql",
                "average_price_per_square_meter_by_property_type": "warehouse/house/select_average_price_per_square_meter_by_room.sql",
            },
        ))
    endpoint_registry.register(
        Key.ONLINE_SHOPPING_REST_API,
        RestApiEndpoint(
            name=Key.ONLINE_SHOPPING_REST_API,
            url=generate_dataset_download_url(main_settings.api["data_simulator"].url, "online_shopping"),
        ))
    endpoint_registry.register(
        Key.ONLINE_SHOPPING_KAFKA_CONSUMER,
        MessagingEndpoint(
            name=Key.ONLINE_SHOPPING_KAFKA_CONSUMER,
            connection_name=Key.ONLINE_SHOPPING_KAFKA_CONSUMER,
            channel_name=main_settings.messaging[Key.ONLINE_SHOPPING_KAFKA_CONSUMER].channel_name,
            bootstrap_servers=main_settings.messaging[Key.ONLINE_SHOPPING_KAFKA_CONSUMER].bootstrap_servers,
            starting_offsets=main_settings.messaging[Key.ONLINE_SHOPPING_KAFKA_CONSUMER].starting_offsets,
        ))
    endpoint_registry.register(
        Key.ONLINE_SHOPPING_DATA_LAKE,
        DataLakeEndpoint(
            name=Key.ONLINE_SHOPPING_DATA_LAKE,
            connection_name=Key.ONLINE_SHOPPING_DATA_LAKE,
            bucket_name=main_settings.data_lake[Key.PLATFORM_DATA_LAKE].bucket_name,
            scheme=main_settings.data_lake[Key.PLATFORM_DATA_LAKE].scheme,
        ))
    endpoint_registry.register(
        Key.ONLINE_SHOPPING_BACKUP_DATA_LAKE,
        DataLakeEndpoint(
            name=Key.ONLINE_SHOPPING_BACKUP_DATA_LAKE,
            connection_name=Key.ONLINE_SHOPPING_DATA_LAKE,
            bucket_name=main_settings.data_lake[Key.PLATFORM_BACKUP_DATA_LAKE].bucket_name,
            scheme=main_settings.data_lake[Key.PLATFORM_BACKUP_DATA_LAKE].scheme,
        ))
    endpoint_registry.register(
        Key.ONLINE_SHOPPING_DATABASE,
        DatabaseEndpoint(
            name=Key.ONLINE_SHOPPING_DATABASE,
            connection_name=Key.ONLINE_SHOPPING_DATABASE,
            schema="online_shopping",
            stage_table_name="online_shopping_stage",
            full_stage_table_name="online_shopping.online_shopping_stage",
            table_names=["online_shopping.online_shopping_stage"],
            create_sql_files={
                "create": "database/online_shopping/create_tables.sql"
            },
            truncate_sql_files={
                "truncate": "database/online_shopping/truncate_stage.sql"
            },
            query_sql_files={"select_all": "database/select_all.sql"},
        ))
    endpoint_registry.register(
        Key.ONLINE_SHOPPING_WAREHOUSE,
        WarehouseEndpoint(
            name=Key.ONLINE_SHOPPING_WAREHOUSE,
            connection_name=Key.ONLINE_SHOPPING_WAREHOUSE,
            schema=main_settings.warehouse[Key.ONLINE_SHOPPING_WAREHOUSE].database_name,
            table_name="online_shopping_table",
            full_table_name=f"{main_settings.warehouse[Key.ONLINE_SHOPPING_WAREHOUSE].database_name}.online_shopping_table",
            create_sql_files={
                "create_database": "warehouse/online_shopping/create_database.sql",
                "create_table": "warehouse/online_shopping/create_table.sql",
            },
            truncate_sql_files={
                "truncate": "warehouse/online_shopping/truncate_warehouse.sql"
            },
            query_sql_files={
                "select_all": "warehouse/select_all.sql",
                "revenue_by_country": "warehouse/online_shopping/select_revenue_by_country.sql",
            },
        ))

    from data_platform.domain.house.dataset import house_dataset
    from data_platform.domain.online_shopping.dataset import ONLINE_SHOPPING_DATASET

    dataset_registry.clear()
    dataset_registry.register(house_dataset.name, house_dataset)
    dataset_registry.register(ONLINE_SHOPPING_DATASET.name, ONLINE_SHOPPING_DATASET)
