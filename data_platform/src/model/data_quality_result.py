from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class SaleDataQualityStatus(StrEnum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"


class DataQualityResult(BaseModel):
    data_quality_result_id: UUID = Field(default_factory=uuid4)
    pipeline_id: str
    task_id: str | None = None
    dataset_name: str
    check_name: str
    check_type: str
    status: SaleDataQualityStatus
    expected_value: str | None = None
    actual_value: str | None = None
    failed_row_count: int | None = None
    sample_failure_uri: str | None = None
    checked_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)
