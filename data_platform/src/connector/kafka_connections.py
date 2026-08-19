from __future__ import annotations

from confluent_kafka import Consumer, Producer

from config.settings import settings as main_settings


def create_sale_publisher_connection() -> Producer:
    return Producer(
        {
            "bootstrap.servers": main_settings.messaging["sale.kafka.listener"].bootstrap_servers,
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
            "bootstrap.servers": main_settings.messaging["house.kafka.listener"].bootstrap_servers,
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
            "bootstrap.servers": main_settings.messaging["audit.kafka.producer"].bootstrap_servers,
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
            "bootstrap.servers": main_settings.messaging["sale.kafka.listener"].bootstrap_servers,
            "group.id": "data-platform-messaging",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )


def create_house_listener_connection() -> Consumer:
    return Consumer(
        {
            "bootstrap.servers": main_settings.messaging["house.kafka.listener"].bootstrap_servers,
            "group.id": "data-platform-messaging",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )


def create_audit_listener_connection() -> Consumer:
    return Consumer(
        {
            "bootstrap.servers": main_settings.messaging["audit.kafka.listener"].bootstrap_servers,
            "group.id": "data-platform-messaging",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )
