from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AuditSettings:
    channel_name: str
    archive_bucket_name: str


settings = AuditSettings(
    channel_name=os.getenv("APP_AUDIT_CHANNEL_NAME", "sale.audit.event.v1"),
    archive_bucket_name=os.getenv("APP_AUDIT_ARCHIVE_BUCKET_NAME", "app-datalake-audit"),
)
