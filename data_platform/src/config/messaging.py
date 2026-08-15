from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class MessagingSettings:
    bootstrap_servers: str
    topic: str
    audit_topic: str
    starting_offsets: str


settings = MessagingSettings(
    bootstrap_servers=os.getenv("APP_STREAMING_BOOTSTRAP_SERVERS", "localhost:9092"),
    topic=os.getenv("APP_STREAMING_TOPIC", "sale-events"),
    audit_topic=os.getenv("APP_STREAMING_AUDIT_TOPIC", "sale.audit.event.v1"),
    starting_offsets=os.getenv("APP_STREAMING_STARTING_OFFSETS", "earliest"),
)

