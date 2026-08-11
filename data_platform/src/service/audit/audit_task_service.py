import time
from collections.abc import Iterator
from contextlib import contextmanager
from uuid import uuid4

from factory.audit_event_factory import create_completed_event, create_failed_event, create_started_event
from model.audit_metrics import AuditMetrics
from model.audit_task_context import AuditTaskContext
from streaming.audit_event_producer import AuditEventProducer
from util.time_utils import elapsed_milliseconds


class AuditTaskService:
    def __init__(self) -> None:
        self.producer = AuditEventProducer()

    @contextmanager
    def audit_task(
            self,
            pipeline_name: str,
            pipeline_id: str,
            task_name: str,
            task_attempt: int
    ) -> Iterator[AuditMetrics]:

        started_at = time.perf_counter()
        metrics = AuditMetrics()
        context = AuditTaskContext(
            pipeline_name=pipeline_name,
            pipeline_id=pipeline_id,
            task_name=task_name,
            task_id=str(uuid4()),
            task_attempt=task_attempt,
            metrics=metrics,
        )

        self.producer.publish(create_started_event(context))

        try:
            yield metrics
        except Exception as error:
            self.producer.publish(create_failed_event(context, elapsed_milliseconds(started_at), error))
        else:
            self.producer.publish(create_completed_event(context, elapsed_milliseconds(started_at)))
