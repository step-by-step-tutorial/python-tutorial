from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PipelineStartedAuditRequestModel:
    pipeline_name: str
    pipeline_id: str
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class PipelineCompletedAuditRequestModel:
    pipeline_name: str
    pipeline_id: str
    duration_ms: int
    input_row_count: int | None = None
    output_row_count: int | None = None
    rejected_row_count: int | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class PipelineFailedAuditRequestModel:
    pipeline_name: str
    pipeline_id: str
    duration_ms: int
    error: Exception
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class TaskStartedAuditRequestModel:
    pipeline_name: str
    pipeline_id: str
    task_name: str
    task_id: str
    task_attempt: int
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class TaskCompletedAuditRequestModel:
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
class TaskFailedAuditRequestModel:
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
class DatasetReadAuditRequestModel:
    source_system: str
    source_uri: str
    row_count: int
    pipeline_name: str | None = None
    pipeline_id: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class DatasetWrittenAuditRequestModel:
    source_system: str
    source_uri: str
    destination_system: str
    destination_uri: str
    row_count: int
    pipeline_name: str | None = None
    pipeline_id: str | None = None
    metadata: dict[str, Any] | None = None
