from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from audit.audit_archive_service import save_event as archive_event
from audit.audit_database_service import AuditDatabaseService
from audit.audit_log_service import AuditLogService
from audit.audit_streaming_service import AuditStreamingService
from model.audit_event import AuditEvent


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
    service: AuditLogService

    def write(self, event: AuditEvent) -> None:
        self.service.log(event)


@dataclass
class ArchiveAuditSink:
    bucket_name: str
    enabled: bool = True

    def write(self, event: AuditEvent) -> None:
        if not self.enabled:
            return

        archive_event(event, bucket_name=self.bucket_name)
