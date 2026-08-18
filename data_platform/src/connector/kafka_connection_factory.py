from __future__ import annotations

import atexit
from typing import Any, Callable

from confluent_kafka import Consumer, Producer

from config.settings import settings as main_settings

registry: dict[str, Any] = {}
factories: dict[str, Callable[[], Any]] = {}


def create_sale_publisher_connection() -> Producer:
    return Producer(
        {
            "bootstrap.servers": main_settings.messaging["sale"].bootstrap_servers,
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
            "bootstrap.servers": main_settings.messaging["house"].bootstrap_servers,
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
            "bootstrap.servers": main_settings.messaging["audit"].bootstrap_servers,
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
            "bootstrap.servers": main_settings.messaging["sale"].bootstrap_servers,
            "group.id": "data-platform-messaging",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )


def create_house_listener_connection() -> Consumer:
    return Consumer(
        {
            "bootstrap.servers": main_settings.messaging["house"].bootstrap_servers,
            "group.id": "data-platform-messaging",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )


def create_audit_listener_connection() -> Consumer:
    return Consumer(
        {
            "bootstrap.servers": main_settings.messaging["audit"].bootstrap_servers,
            "group.id": "data-platform-messaging",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )


factories["sale.kafka.producer"] = create_sale_publisher_connection
factories["house.kafka.producer"] = create_house_publisher_connection
factories["audit.kafka.producer"] = create_audit_publisher_connection
factories["sale.kafka.listener"] = create_sale_listener_connection
factories["house.kafka.listener"] = create_house_listener_connection
factories["audit.kafka.listener"] = create_audit_listener_connection


def get_connection(name: str):
    if name not in registry:
        registry[name] = factories[name]()
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
