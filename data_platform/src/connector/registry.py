from __future__ import annotations

import atexit
from typing import Any, Callable

from connector.database_connection_factory import create_audit_connection as create_database_audit_connection
from connector.database_connection_factory import create_house_connection as create_database_house_connection
from connector.database_connection_factory import create_sale_connection as create_database_sale_connection
from connector.datalake_connection_factory import create_audit_connection as create_datalake_audit_connection
from connector.datalake_connection_factory import create_house_connection as create_datalake_house_connection
from connector.datalake_connection_factory import create_sale_connection as create_datalake_sale_connection
from connector.datawarehouse_connection_factory import create_audit_connection as create_datawarehouse_audit_connection
from connector.datawarehouse_connection_factory import create_house_connection as create_datawarehouse_house_connection
from connector.datawarehouse_connection_factory import create_sale_connection as create_datawarehouse_sale_connection
from connector.kafka_connection_factory import create_audit_listener_connection
from connector.kafka_connection_factory import create_audit_publisher_connection
from connector.kafka_connection_factory import create_house_listener_connection
from connector.kafka_connection_factory import create_house_publisher_connection
from connector.kafka_connection_factory import create_sale_listener_connection
from connector.kafka_connection_factory import create_sale_publisher_connection

registry: dict[str, Any] = {}
factories: dict[str, Callable[[], Any]] = {
    "sale.database": create_database_sale_connection,
    "house.database": create_database_house_connection,
    "audit.database": create_database_audit_connection,
    "sale.datalake": create_datalake_sale_connection,
    "house.datalake": create_datalake_house_connection,
    "audit.datalake": create_datalake_audit_connection,
    "sale.datawarehouse": create_datawarehouse_sale_connection,
    "house.datawarehouse": create_datawarehouse_house_connection,
    "audit.datawarehouse": create_datawarehouse_audit_connection,
    "sale.kafka.producer": create_sale_publisher_connection,
    "house.kafka.producer": create_house_publisher_connection,
    "audit.kafka.producer": create_audit_publisher_connection,
    "sale.kafka.listener": create_sale_listener_connection,
    "house.kafka.listener": create_house_listener_connection,
    "audit.kafka.listener": create_audit_listener_connection,
}


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
