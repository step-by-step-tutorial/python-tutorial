from dataclasses import dataclass, field
from typing import Any


@dataclass
class AuditMetrics:
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
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SaleReconciliationMetrics:
    kafka_consumed_count: int
    bronze_row_count: int
    silver_row_count: int
    rejected_row_count: int
    database_written_count: int
