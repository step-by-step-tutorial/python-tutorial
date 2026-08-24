import traceback
from dataclasses import dataclass
from typing import Any

from data_platform.audit.audit_event import AuditEvent, AuditEventType, AuditStatus


@dataclass(frozen=True)
class PipelineStartedAuditRequest:
    pipeline_name: str
    pipeline_id: str
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class PipelineCompletedAuditRequest:
    pipeline_name: str
    pipeline_id: str
    duration_ms: int
    input_row_count: int | None = None
    output_row_count: int | None = None
    rejected_row_count: int | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class PipelineFailedAuditRequest:
    pipeline_name: str
    pipeline_id: str
    duration_ms: int
    error: Exception
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class TaskStartedAuditRequest:
    pipeline_name: str
    pipeline_id: str
    task_name: str
    task_id: str
    task_attempt: int
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class TaskCompletedAuditRequest:
    pipeline_name: str
    pipeline_id: str
    task_name: str
    task_id: str
    task_attempt: int
    duration_ms: int
    input_row_count: int | None = None
    output_row_count: int | None = None
    rejected_row_count: int | None = None
    duplicate_row_count: int | None = None
    source_system: str | None = None
    source_uri: str | None = None
    destination_system: str | None = None
    destination_uri: str | None = None
    schema_version: str | None = None
    checksum: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class TaskFailedAuditRequest:
    pipeline_name: str
    pipeline_id: str
    task_name: str
    task_id: str
    task_attempt: int
    duration_ms: int
    error: Exception
    input_row_count: int | None = None
    output_row_count: int | None = None
    rejected_row_count: int | None = None
    duplicate_row_count: int | None = None
    source_system: str | None = None
    source_uri: str | None = None
    destination_system: str | None = None
    destination_uri: str | None = None
    schema_version: str | None = None
    checksum: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class DatasetReadAuditRequest:
    source_system: str
    source_uri: str
    row_count: int
    pipeline_name: str | None = None
    pipeline_id: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class DatasetWrittenAuditRequest:
    source_system: str
    source_uri: str
    destination_system: str
    destination_uri: str
    row_count: int
    pipeline_name: str | None = None
    pipeline_id: str | None = None
    metadata: dict[str, Any] | None = None


class AuditEventFactory:

    @staticmethod
    def create_pipeline_started_event(request: PipelineStartedAuditRequest) -> AuditEvent:
        return AuditEvent(
            event_type=AuditEventType.PIPELINE_STARTED,
            pipeline_name=request.pipeline_name,
            pipeline_id=request.pipeline_id,
            status=AuditStatus.STARTED,
            metadata=request.metadata or {},
        )

    @staticmethod
    def create_pipeline_completed_event(request: PipelineCompletedAuditRequest) -> AuditEvent:
        return AuditEvent(
            event_type=AuditEventType.PIPELINE_COMPLETED,
            pipeline_name=request.pipeline_name,
            pipeline_id=request.pipeline_id,
            status=AuditStatus.SUCCEEDED,
            input_row_count=request.input_row_count,
            output_row_count=request.output_row_count,
            rejected_row_count=request.rejected_row_count,
            duration_ms=request.duration_ms,
            metadata=request.metadata or {},
        )

    @staticmethod
    def create_pipeline_failed_event(request: PipelineFailedAuditRequest) -> AuditEvent:
        return AuditEvent(
            event_type=AuditEventType.PIPELINE_FAILED,
            pipeline_name=request.pipeline_name,
            pipeline_id=request.pipeline_id,
            status=AuditStatus.FAILED,
            duration_ms=request.duration_ms,
            error_type=type(request.error).__name__,
            error_message=str(request.error),
            error_stacktrace="".join(
                traceback.format_exception(type(request.error), request.error, request.error.__traceback__)
            ),
            metadata=request.metadata or {},
        )

    @staticmethod
    def create_task_started_event(request: TaskStartedAuditRequest) -> AuditEvent:
        return AuditEvent(
            event_type=AuditEventType.TASK_STARTED,
            pipeline_name=request.pipeline_name,
            pipeline_id=request.pipeline_id,
            task_name=request.task_name,
            task_id=request.task_id,
            task_attempt=request.task_attempt,
            status=AuditStatus.STARTED,
            metadata=request.metadata or {},
        )

    @staticmethod
    def create_task_completed_event(request: TaskCompletedAuditRequest) -> AuditEvent:
        return AuditEvent(
            event_type=AuditEventType.TASK_COMPLETED,
            pipeline_name=request.pipeline_name,
            pipeline_id=request.pipeline_id,
            task_name=request.task_name,
            task_id=request.task_id,
            task_attempt=request.task_attempt,
            status=AuditStatus.SUCCEEDED,
            duration_ms=request.duration_ms,
            input_row_count=request.input_row_count,
            output_row_count=request.output_row_count,
            rejected_row_count=request.rejected_row_count,
            duplicate_row_count=request.duplicate_row_count,
            source_system=request.source_system,
            source_uri=request.source_uri,
            destination_system=request.destination_system,
            destination_uri=request.destination_uri,
            schema_version=request.schema_version,
            checksum=request.checksum,
            metadata=request.metadata or {},
        )

    @staticmethod
    def create_task_failed_event(request: TaskFailedAuditRequest) -> AuditEvent:
        return AuditEvent(
            event_type=AuditEventType.TASK_FAILED,
            pipeline_name=request.pipeline_name,
            pipeline_id=request.pipeline_id,
            task_name=request.task_name,
            task_id=request.task_id,
            task_attempt=request.task_attempt,
            status=AuditStatus.FAILED,
            duration_ms=request.duration_ms,
            input_row_count=request.input_row_count,
            output_row_count=request.output_row_count,
            rejected_row_count=request.rejected_row_count,
            duplicate_row_count=request.duplicate_row_count,
            source_system=request.source_system,
            source_uri=request.source_uri,
            destination_system=request.destination_system,
            destination_uri=request.destination_uri,
            schema_version=request.schema_version,
            checksum=request.checksum,
            error_type=type(request.error).__name__,
            error_message=str(request.error),
            error_stacktrace="".join(
                traceback.format_exception(type(request.error), request.error, request.error.__traceback__)
            ),
            metadata=request.metadata or {},
        )

    @staticmethod
    def create_dataset_read_event(request: DatasetReadAuditRequest) -> AuditEvent:
        return AuditEvent(
            event_type=AuditEventType.DATASET_READ,
            pipeline_name=request.pipeline_name or "",
            pipeline_id=request.pipeline_id or "",
            status=AuditStatus.SUCCEEDED,
            source_system=request.source_system,
            source_uri=request.source_uri,
            input_row_count=request.row_count,
            metadata=request.metadata or {},
        )

    @staticmethod
    def create_dataset_written_event(request: DatasetWrittenAuditRequest) -> AuditEvent:
        return AuditEvent(
            event_type=AuditEventType.DATASET_WRITTEN,
            pipeline_name=request.pipeline_name or "",
            pipeline_id=request.pipeline_id or "",
            status=AuditStatus.SUCCEEDED,
            source_system=request.source_system,
            source_uri=request.source_uri,
            destination_system=request.destination_system,
            destination_uri=request.destination_uri,
            output_row_count=request.row_count,
            metadata=request.metadata or {},
        )

