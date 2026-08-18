import time
from uuid import uuid4

from audit.audit_archive_service import AuditArchiveService
from audit.audit_database_service import AuditDatabaseService
from audit.audit_event_factory import AuditEventFactory
from audit.audit_log_service import AuditLogService
from audit.audit_messaging_service import AuditMessagingService
from dataset.definition import AuditEndpoint
from util.time_utils import elapsed_milliseconds


class AuditService:

    def __init__(self, audit_endpoint: AuditEndpoint ) -> None:
        self._audit_endpoint = audit_endpoint
        self._log_service = AuditLogService()
        self._database_service = AuditDatabaseService(self._audit_endpoint)
        self._messaging_service = AuditMessagingService(self._audit_endpoint)
        self._archive_service = AuditArchiveService(self._audit_endpoint)

    def _emit(self, event) -> None:
        self._log_service.write(event)
        self._database_service.write(event)
        self._messaging_service.write(event)
        self._archive_service.write(event)

    def start_pipeline(self, pipeline_name: str, pipeline_id: str, metadata: dict | None = None) -> float:
        started_at = time.perf_counter()
        event = AuditEventFactory.create_pipeline_started_event(pipeline_name, pipeline_id, metadata)
        self._emit(event)
        return started_at

    def complete_pipeline(
            self,
            pipeline_name: str,
            pipeline_id: str,
            started_at: float,
            input_row_count: int | None = None,
            output_row_count: int | None = None,
            rejected_row_count: int | None = None,
            metadata: dict | None = None
    ) -> None:
        event = AuditEventFactory.create_pipeline_completed_event(
            pipeline_name=pipeline_name,
            pipeline_id=pipeline_id,
            duration_ms=elapsed_milliseconds(started_at),
            input_row_count=input_row_count,
            output_row_count=output_row_count,
            rejected_row_count=rejected_row_count,
            metadata=metadata
        )
        self._emit(event)

    def fail_pipeline(
            self,
            pipeline_name: str,
            pipeline_id: str,
            started_at: float,
            error: Exception,
            metadata: dict | None = None
    ) -> None:
        event = AuditEventFactory.create_pipeline_failed_event(
            pipeline_name=pipeline_name,
            pipeline_id=pipeline_id,
            duration_ms=elapsed_milliseconds(started_at),
            error=error,
            metadata=metadata
        )
        self._emit(event)

    def start_task(
            self,
            pipeline_name: str,
            pipeline_id: str,
            task_name: str,
            task_attempt: int,
            metadata: dict | None = None
    ) -> tuple[str, float]:
        started_at = time.perf_counter()
        task_id = str(uuid4())
        event = AuditEventFactory.create_task_started_event(
            pipeline_name=pipeline_name,
            pipeline_id=pipeline_id,
            task_name=task_name,
            task_id=task_id,
            task_attempt=task_attempt,
            metadata=metadata
        )
        self._emit(event)

        return task_id, started_at

    def complete_task(
            self,
            pipeline_name: str,
            pipeline_id: str,
            task_name: str,
            task_id: str,
            task_attempt: int,
            started_at: float,
            input_row_count: int | None = None,
            output_row_count: int | None = None,
            rejected_row_count: int | None = None,
            duplicate_row_count: int | None = None,
            source_system: str | None = None,
            source_uri: str | None = None,
            destination_system: str | None = None,
            destination_uri: str | None = None,
            schema_version: str | None = None,
            checksum: str | None = None,
            metadata: dict | None = None
    ) -> None:
        event = AuditEventFactory.create_task_completed_event(
            pipeline_name=pipeline_name,
            pipeline_id=pipeline_id,
            task_name=task_name,
            task_id=task_id,
            task_attempt=task_attempt,
            duration_ms=elapsed_milliseconds(started_at),
            input_row_count=input_row_count,
            output_row_count=output_row_count,
            rejected_row_count=rejected_row_count,
            duplicate_row_count=duplicate_row_count,
            source_system=source_system,
            source_uri=source_uri,
            destination_system=destination_system,
            destination_uri=destination_uri,
            schema_version=schema_version,
            checksum=checksum,
            metadata=metadata
        )
        self._emit(event)

    def fail_task(
            self,
            pipeline_name: str,
            pipeline_id: str,
            task_name: str,
            task_id: str,
            task_attempt: int,
            started_at: float,
            error: Exception,
            input_row_count: int | None = None,
            output_row_count: int | None = None,
            rejected_row_count: int | None = None,
            duplicate_row_count: int | None = None,
            source_system: str | None = None,
            source_uri: str | None = None,
            destination_system: str | None = None,
            destination_uri: str | None = None,
            schema_version: str | None = None,
            checksum: str | None = None,
            metadata: dict | None = None
    ) -> None:
        event = AuditEventFactory.create_task_failed_event(
            pipeline_name=pipeline_name,
            pipeline_id=pipeline_id,
            task_name=task_name,
            task_id=task_id,
            task_attempt=task_attempt,
            duration_ms=elapsed_milliseconds(started_at),
            error=error,
            input_row_count=input_row_count,
            output_row_count=output_row_count,
            rejected_row_count=rejected_row_count,
            duplicate_row_count=duplicate_row_count,
            source_system=source_system,
            source_uri=source_uri,
            destination_system=destination_system,
            destination_uri=destination_uri,
            schema_version=schema_version,
            checksum=checksum,
            metadata=metadata
        )
        self._emit(event)

    def read_dataset(
            self,
            source_system: str,
            source_uri: str,
            row_count: int,
            pipeline_name: str | None = None,
            pipeline_id: str | None = None,
            metadata: dict | None = None
    ) -> None:
        event = AuditEventFactory.create_dataset_read_event(
            source_system=source_system,
            source_uri=source_uri,
            row_count=row_count,
            pipeline_name=pipeline_name,
            pipeline_id=pipeline_id,
            metadata=metadata
        )
        self._emit(event)

    def write_dataset(
            self,
            source_system: str,
            source_uri: str,
            destination_system: str,
            destination_uri: str,
            row_count: int,
            pipeline_name: str | None = None,
            pipeline_id: str | None = None,
            metadata: dict | None = None
    ) -> None:
        event = AuditEventFactory.create_dataset_written_event(
            source_system=source_system,
            source_uri=source_uri,
            destination_system=destination_system,
            destination_uri=destination_uri,
            row_count=row_count,
            pipeline_name=pipeline_name,
            pipeline_id=pipeline_id,
            metadata=metadata
        )
        self._emit(event)
