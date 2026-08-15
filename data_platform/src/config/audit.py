from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AuditSettings:
    archive_enabled: bool
    streaming_topic: str
    archive_bucket_name: str


settings = AuditSettings(
    archive_enabled=os.getenv("APP_AUDIT_ARCHIVE_ENABLED", "true").lower() in {"1", "true", "yes", "on"},
    streaming_topic=os.getenv("APP_STREAMING_AUDIT_TOPIC", "sale.audit.event.v1"),
    archive_bucket_name=os.getenv("APP_DATALAKE_AUDIT_BUCKET_NAME", "app-datalake-audit"),
)

