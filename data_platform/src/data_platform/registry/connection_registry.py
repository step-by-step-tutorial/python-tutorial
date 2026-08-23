import atexit
from typing import Any

import data_platform.connector.data_lake_connections
import data_platform.connector.data_warehouse_connections
import data_platform.connector.database_connections
import data_platform.connector.kafka_connections
from data_platform.config.keys import Key
from data_platform.registry.base_registry import Registry


class ConnectionRegistry(Registry[Any]):
    def __init__(self) -> None:
        super().__init__("connection")

    def close(self, name: str) -> None:
        if not self.contains(name):
            return

        connection = self.get_item(name)
        self.remove(name)

        if hasattr(connection, "flush") and callable(connection.flush):
            connection.flush()
        if hasattr(connection, "dispose") and callable(connection.dispose):
            connection.dispose()
        elif hasattr(connection, "close") and callable(connection.close):
            connection.close()

    def close_all(self) -> None:
        for name in self.loaded_names():
            self.close(name)


connection_registry = ConnectionRegistry()

connection_registry.register_lazy_item(
    Key.SALE_DATABASE,
    data_platform.connector.database_connections.create_sale_connection
)
connection_registry.register_lazy_item(
    Key.HOUSE_DATABASE,
    data_platform.connector.database_connections.create_house_connection
)
connection_registry.register_lazy_item(
    Key.AUDIT_DATABASE,
    data_platform.connector.database_connections.create_audit_connection
)
connection_registry.register_lazy_item(
    Key.SALE_DATA_LAKE,
    data_platform.connector.data_lake_connections.create_sale_connection
)
connection_registry.register_lazy_item(
    Key.HOUSE_DATA_LAKE,
    data_platform.connector.data_lake_connections.create_house_connection
)
connection_registry.register_lazy_item(
    Key.AUDIT_DATA_LAKE,
    data_platform.connector.data_lake_connections.create_audit_connection
)
connection_registry.register_lazy_item(
    Key.SALE_DATA_WAREHOUSE,
    data_platform.connector.data_warehouse_connections.create_sale_connection
)
connection_registry.register_lazy_item(
    Key.HOUSE_DATA_WAREHOUSE,
    data_platform.connector.data_warehouse_connections.create_house_connection
)
connection_registry.register_lazy_item(
    Key.AUDIT_DATA_WAREHOUSE,
    data_platform.connector.data_warehouse_connections.create_audit_connection
)
connection_registry.register_lazy_item(
    Key.SALE_KAFKA_PRODUCER,
    data_platform.connector.kafka_connections.create_sale_publisher_connection
)
connection_registry.register_lazy_item(
    Key.HOUSE_KAFKA_PRODUCER,
    data_platform.connector.kafka_connections.create_house_publisher_connection
)
connection_registry.register_lazy_item(
    Key.AUDIT_KAFKA_PRODUCER,
    data_platform.connector.kafka_connections.create_audit_publisher_connection
)
connection_registry.register_lazy_item(
    Key.SALE_KAFKA_CONSUMER,
    data_platform.connector.kafka_connections.create_sale_listener_connection
)
connection_registry.register_lazy_item(
    Key.HOUSE_KAFKA_CONSUMER,
    data_platform.connector.kafka_connections.create_house_listener_connection
)
connection_registry.register_lazy_item(
    Key.AUDIT_KAFKA_CONSUMER,
    data_platform.connector.kafka_connections.create_audit_listener_connection
)

atexit.register(connection_registry.close_all)
