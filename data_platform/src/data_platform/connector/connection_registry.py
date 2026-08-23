import atexit
from typing import Any, Callable

import data_platform.connector.database_connections
import data_platform.connector.datalake_connections
import data_platform.connector.datawarehouse_connections
import data_platform.connector.kafka_connections
from data_platform.keys import Key

factories: dict[str, Callable[[], Any]] = {
    Key.SALE_DATABASE: data_platform.connector.database_connections.create_sale_connection,
    Key.HOUSE_DATABASE: data_platform.connector.database_connections.create_house_connection,
    Key.AUDIT_DATABASE: data_platform.connector.database_connections.create_audit_connection,
    Key.SALE_DATALAKE: data_platform.connector.datalake_connections.create_sale_connection,
    Key.HOUSE_DATALAKE: data_platform.connector.datalake_connections.create_house_connection,
    Key.AUDIT_DATALAKE: data_platform.connector.datalake_connections.create_audit_connection,
    Key.SALE_DATAWAREHOUSE: data_platform.connector.datawarehouse_connections.create_sale_connection,
    Key.HOUSE_DATAWAREHOUSE: data_platform.connector.datawarehouse_connections.create_house_connection,
    Key.AUDIT_DATAWAREHOUSE: data_platform.connector.datawarehouse_connections.create_audit_connection,
    Key.SALE_KAFKA_PRODUCER: data_platform.connector.kafka_connections.create_sale_publisher_connection,
    Key.HOUSE_KAFKA_PRODUCER: data_platform.connector.kafka_connections.create_house_publisher_connection,
    Key.AUDIT_KAFKA_PRODUCER: data_platform.connector.kafka_connections.create_audit_publisher_connection,
    Key.SALE_KAFKA_LISTENER: data_platform.connector.kafka_connections.create_sale_listener_connection,
    Key.HOUSE_KAFKA_LISTENER: data_platform.connector.kafka_connections.create_house_listener_connection,
    Key.AUDIT_KAFKA_LISTENER: data_platform.connector.kafka_connections.create_audit_listener_connection,
}

registry: dict[str, Any] = {}


def get_connection(name: str) -> Any:
    if name not in registry:
        registry[name] = factories[name]()
    return registry[name]


def close_connection(name: str) -> None:
    connection = registry.pop(name, None)
    if connection is None:
        return

    if hasattr(connection, "flush") and callable(connection.flush):
        connection.flush()
    if hasattr(connection, "dispose") and callable(connection.dispose):
        connection.dispose()
    elif hasattr(connection, "close") and callable(connection.close):
        connection.close()


def close_all_connections() -> None:
    for name in list(registry):
        close_connection(name)


atexit.register(close_all_connections)
