from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class MessagingSettings:
    bootstrap_servers: str
    channel_name: str
    audit_channel_name: str


sale_settings = MessagingSettings(
    bootstrap_servers=os.getenv("APP_SALE_STREAMING_BOOTSTRAP_SERVERS", "localhost:9092"),
    channel_name=os.getenv("APP_SALE_CHANNEL_NAME", "sale-events"),
    audit_channel_name=os.getenv("APP_SALE_AUDIT_CHANNEL_NAME", "sale.audit.event.v1"),
)
house_settings = MessagingSettings(
    bootstrap_servers=os.getenv("APP_HOUSE_STREAMING_BOOTSTRAP_SERVERS", "localhost:9092"),
    channel_name=os.getenv("APP_HOUSE_CHANNEL_NAME", "house-events"),
    audit_channel_name=os.getenv("APP_HOUSE_AUDIT_CHANNEL_NAME", "house.audit.event.v1"),
)
audit_settings = MessagingSettings(
    bootstrap_servers=os.getenv("APP_AUDIT_STREAMING_BOOTSTRAP_SERVERS", "localhost:9092"),
    channel_name=os.getenv("APP_AUDIT_STREAM_CHANNEL_NAME", "audit-events"),
    audit_channel_name=os.getenv("APP_AUDIT_AUDIT_CHANNEL_NAME", "sale.audit.event.v1"),
)

settings = sale_settings
