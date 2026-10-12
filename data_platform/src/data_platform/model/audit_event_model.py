import json
import traceback
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from data_platform.model.audit_request_model import (
    DatasetReadAuditRequestModel,
    DatasetWrittenAuditRequestModel,
    PipelineCompletedAuditRequestModel,
    PipelineFailedAuditRequestModel,
    PipelineStartedAuditRequestModel,
    TaskCompletedAuditRequestModel,
    TaskFailedAuditRequestModel,
    TaskStartedAuditRequestModel,
)


class AuditEventType(StrEnum):
    PIPELINE_STARTED = "PIPELINE_STARTED"
    PIPELINE_COMPLETED = "PIPELINE_COMPLETED"
    PIPELINE_FAILED = "PIPELINE_FAILED"
    TASK_STARTED = "TASK_STARTED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_FAILED = "TASK_FAILED"
    DATASET_READ = "DATASET_READ"
    DATASET_WRITTEN = "DATASET_WRITTEN"
    DATA_QUALITY_CHECKED = "DATA_QUALITY_CHECKED"
    RECONCILIATION_COMPLETED = "RECONCILIATION_COMPLETED"


class AuditStatus(StrEnum):
    STARTED = "STARTED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    WARNING = "WARNING"


def _error_fields(error: Exception) -> dict[str, str]:
    return {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "error_stacktrace": "".join(traceback.format_exception(type(error), error, error.__traceback__)),
    }


class AuditEventModel(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    event_version: int = 1
    event_type: AuditEventType
    event_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
    pipeline_name: str
    pipeline_id: str
    task_name: str | None = None
    task_id: str | None = None
    task_attempt: int | None = None
    status: AuditStatus
    source_system: str | None = None
    source_uri: str | None = None
    destination_system: str | None = None
    destination_uri: str | None = None
    input_row_count: int | None = None
    output_row_count: int | None = None
    rejected_row_count: int | None = None
    duplicate_row_count: int | None = None
    schema_version: str | None = None
    checksum: str | None = None
    duration_ms: int | None = None
    error_type: str | None = None
    error_message: str | None = None
    error_stacktrace: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_pipeline_started(cls, request: PipelineStartedAuditRequestModel) -> "AuditEventModel":
        return cls(
            event_type=AuditEventType.PIPELINE_STARTED,
            pipeline_name=request.pipeline_name,
            pipeline_id=request.pipeline_id,
            status=AuditStatus.STARTED,
            metadata=request.metadata or {},
        )

    @classmethod
    def from_pipeline_completed(cls, request: PipelineCompletedAuditRequestModel) -> "AuditEventModel":
        return cls(
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

    @classmethod
    def from_pipeline_failed(cls, request: PipelineFailedAuditRequestModel) -> "AuditEventModel":
        return cls(
            event_type=AuditEventType.PIPELINE_FAILED,
            pipeline_name=request.pipeline_name,
            pipeline_id=request.pipeline_id,
            status=AuditStatus.FAILED,
            duration_ms=request.duration_ms,
            **_error_fields(request.error),
            metadata=request.metadata or {},
        )

    @classmethod
    def from_task_started(cls, request: TaskStartedAuditRequestModel) -> "AuditEventModel":
        return cls(
            event_type=AuditEventType.TASK_STARTED,
            pipeline_name=request.pipeline_name,
            pipeline_id=request.pipeline_id,
            task_name=request.task_name,
            task_id=request.task_id,
            task_attempt=request.task_attempt,
            status=AuditStatus.STARTED,
            metadata=request.metadata or {},
        )

    @classmethod
    def from_task_completed(cls, request: TaskCompletedAuditRequestModel) -> "AuditEventModel":
        return cls(
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

    @classmethod
    def from_task_failed(cls, request: TaskFailedAuditRequestModel) -> "AuditEventModel":
        return cls(
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
            **_error_fields(request.error),
            metadata=request.metadata or {},
        )

    @classmethod
    def from_dataset_read(cls, request: DatasetReadAuditRequestModel) -> "AuditEventModel":
        return cls(
            event_type=AuditEventType.DATASET_READ,
            pipeline_name=request.pipeline_name or "",
            pipeline_id=request.pipeline_id or "",
            status=AuditStatus.SUCCEEDED,
            source_system=request.source_system,
            source_uri=request.source_uri,
            input_row_count=request.row_count,
            metadata=request.metadata or {},
        )

    @classmethod
    def from_dataset_written(cls, request: DatasetWrittenAuditRequestModel) -> "AuditEventModel":
        return cls(
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

    def to_persistable(self) -> dict[str, Any]:
        parameters = self.model_dump(mode="json")
        parameters["metadata"] = json.dumps(parameters["metadata"])
        return parameters
