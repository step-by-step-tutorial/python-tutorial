from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


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


class AuditEvent(BaseModel):
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
