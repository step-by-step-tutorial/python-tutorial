from functools import partial

from data_platform.config.key import Key
from data_platform.config.settings import settings
from data_platform.connector.database_connector import create_database_engine
from data_platform.connector.datalake_connector import create_datalake_client
from data_platform.connector.kafka_connector import create_consumer, create_producer
from data_platform.connector.warehouse_connector import create_warehouse_client
from data_platform.model.endpoint_model import AuditEndpointModel
from data_platform.registry.connection_registry import connection_registry
from data_platform.registry.endpoint_registry import endpoint_registry


def register_audit() -> None:
    data_lake = settings.data_lake[Key.AUDIT_DATA_LAKE]
    messaging = settings.messaging[Key.AUDIT_MESSAGING]

    connection_registry.register_lazy_item(
        Key.AUDIT_DATABASE, partial(create_database_engine, settings.database[Key.AUDIT_DATABASE]))
    connection_registry.register_lazy_item(Key.AUDIT_DATA_LAKE, partial(create_datalake_client, data_lake))
    connection_registry.register_lazy_item(
        Key.AUDIT_WAREHOUSE, partial(create_warehouse_client, settings.warehouse[Key.AUDIT_WAREHOUSE]))
    connection_registry.register_lazy_item(Key.AUDIT_KAFKA_PRODUCER, partial(create_producer, messaging))
    connection_registry.register_lazy_item(Key.AUDIT_KAFKA_CONSUMER, partial(create_consumer, messaging))

    endpoint_registry.register(
        Key.AUDIT,
        AuditEndpointModel(
            database_connection_name=Key.AUDIT_DATABASE,
            messaging_connection_name=Key.AUDIT_KAFKA_PRODUCER,
            datalake_connection_name=Key.AUDIT_DATA_LAKE,
            schema="audit",
            create_sql_files={"create": "database/audit/create_tables.sql"},
            write_sql_files={"write": "database/audit/insert_event.sql"},
            channel_name=messaging.channel_name,
            bootstrap_servers=messaging.bootstrap_servers,
            bucket_name=data_lake.bucket_name,
        ),
    )
