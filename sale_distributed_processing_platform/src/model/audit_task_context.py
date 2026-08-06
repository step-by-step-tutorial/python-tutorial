from dataclasses import dataclass

from model.audit_metrics import AuditMetrics


@dataclass(frozen=True)
class AuditTaskContext:
    pipeline_name: str
    pipeline_id: str
    task_name: str
    task_id: str
    task_attempt: int
    metrics: AuditMetrics