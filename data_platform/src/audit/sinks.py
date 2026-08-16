from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol

import audit.audit_archive_service as audit_archive_service
from audit.audit_database_service import AuditDatabaseService
from audit.audit_streaming_service import AuditStreamingService
from model.audit_event import AuditEvent

logger = logging.getLogger(__name__)


class AuditSink(Protocol):
    def write(self, event: AuditEvent) -> None:
        ...


@dataclass
class DatabaseAuditSink:
    topic: str
    service: AuditDatabaseService

    def write(self, event: AuditEvent) -> None:
        self.service.save(event, self.topic)


@dataclass
class StreamingAuditSink:
    service: AuditStreamingService

    def write(self, event: AuditEvent) -> None:
        self.service.publish(event)


@dataclass
class LogAuditSink:
    def write(self, event: AuditEvent) -> None:
        logger.info("Audit event: %s", event.event_id)


@dataclass
class ArchiveAuditSink:
    bucket_name: str
    enabled: bool = True

    def write(self, event: AuditEvent) -> None:
        if not self.enabled:
            return

        audit_archive_service.save_event(event, bucket_name=self.bucket_name)
