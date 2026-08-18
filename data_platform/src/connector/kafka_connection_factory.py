from __future__ import annotations

import atexit
from typing import Any

from confluent_kafka import Consumer, Producer

from config.messaging import audit_settings, house_settings, sale_settings

registry: dict[str, Any] = {}


def create_sale_publisher_connection() -> Producer:
    return Producer(
        {
            "bootstrap.servers": sale_settings.bootstrap_servers,
            "enable.idempotence": True,
            "acks": "all",
            "retries": 10,
            "delivery.timeout.ms": 120_000,
            "linger.ms": 10,
        }
    )


def create_house_publisher_connection() -> Producer:
    return Producer(
        {
            "bootstrap.servers": house_settings.bootstrap_servers,
            "enable.idempotence": True,
            "acks": "all",
            "retries": 10,
            "delivery.timeout.ms": 120_000,
            "linger.ms": 10,
        }
    )


def create_audit_publisher_connection() -> Producer:
    return Producer(
        {
            "bootstrap.servers": audit_settings.bootstrap_servers,
            "enable.idempotence": True,
            "acks": "all",
            "retries": 10,
            "delivery.timeout.ms": 120_000,
            "linger.ms": 10,
        }
    )


def create_sale_listener_connection() -> Consumer:
    return Consumer(
        {
            "bootstrap.servers": sale_settings.bootstrap_servers,
            "group.id": "data-platform-messaging",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )


def create_house_listener_connection() -> Consumer:
    return Consumer(
        {
            "bootstrap.servers": house_settings.bootstrap_servers,
            "group.id": "data-platform-messaging",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )


def create_audit_listener_connection() -> Consumer:
    return Consumer(
        {
            "bootstrap.servers": audit_settings.bootstrap_servers,
            "group.id": "data-platform-messaging",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )


registry["sale.kafka.producer"] = create_sale_publisher_connection()
registry["house.kafka.producer"] = create_house_publisher_connection()
registry["audit.kafka.producer"] = create_audit_publisher_connection()
registry["sale.kafka.listener"] = create_sale_listener_connection()
registry["house.kafka.listener"] = create_house_listener_connection()
registry["audit.kafka.listener"] = create_audit_listener_connection()


def get_connection(name: str):
    return registry[name]


def close_connection(name: str) -> None:
    connection = registry.pop(name, None)
    if connection is None:
        return
    if hasattr(connection, "flush") and callable(connection.flush):
        connection.flush()
    if hasattr(connection, "close") and callable(connection.close):
        connection.close()


def close_all_connections() -> None:
    for name in list(registry):
        close_connection(name)


atexit.register(close_all_connections)
