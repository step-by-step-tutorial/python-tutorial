import time
from abc import ABC, abstractmethod
from typing import Any, Callable

from data_platform.audit.audit_event_factory import (
    AuditEventFactory, PipelineCompletedAuditRequest,
    PipelineFailedAuditRequest,
    PipelineStartedAuditRequest,
    TaskCompletedAuditRequest,
    TaskFailedAuditRequest,
    TaskStartedAuditRequest,
)
from data_platform.audit.audit_service import AuditService
from data_platform.model.dataset import Dataset
from data_platform.util.pipeline_utils import create_pipeline_id
from data_platform.util.time_utils import elapsed_milliseconds, generate_ingestion_time


class Pipeline(ABC):

    def __init__(self, dataset: Dataset) -> None:
        self.dataset = dataset
        self.pipeline_name = dataset.name
        self.pipeline_id = create_pipeline_id()
        self.ingestion_time = generate_ingestion_time()
        self._started_at = None
        self._audit_service = AuditService(dataset.audit)

    @abstractmethod
    def prepare(self) -> None:
        ...

    @abstractmethod
    def ingest(self) -> str:
        ...

    @abstractmethod
    def clean(self, path: str) -> str:
        ...

    @abstractmethod
    def validate(self, path: str) -> str:
        ...

    @abstractmethod
    def enrich(self, path: str) -> str:
        ...

    @abstractmethod
    def expose(self, path: str) -> None:
        ...

    @abstractmethod
    def analyze(self, path: str) -> None:
        ...

    @abstractmethod
    def cleanup(self) -> None:
        ...

    def run_step(self, step_name: str, action: Callable[[], Any]) -> Any:
        self.dataset.flow.before_step(step_name)
        step_id = f"{self.pipeline_id}-{step_name}"
        started_at = time.perf_counter()
        self.start_task(step_id, step_name)
        try:
            result = action()
        except Exception as error:
            self.fail_task(step_name, step_id, error, started_at)
            raise
        self.complete_task(step_name, step_id, started_at)
        self.dataset.flow.after_stage(step_name)
        return result

    def run(self) -> None:
        try:
            self.start_pipeline()
            self.run_step("prepare", self.prepare)
            raw_paths = self.run_step("ingest", self.ingest)
            cleaned_paths = self.run_step("clean", lambda: self.clean(raw_paths))
            validated_path = self.run_step("validate", lambda: self.validate(cleaned_paths))
            enriched_paths = self.run_step("enrich", lambda: self.enrich(validated_path))
            self.run_step("expose", lambda: self.expose(enriched_paths))
            self.run_step("analyze", lambda: self.analyze(enriched_paths))
            self.complete_pipeline()
        except Exception as error:
            self.fail_pipeline(error)
            raise
        finally:
            self.run_step("cleanup", self.cleanup)

    def start_pipeline(self) -> None:
        self._started_at = time.perf_counter()
        event = AuditEventFactory.create_pipeline_started_event(
            PipelineStartedAuditRequest(
                pipeline_name=self.pipeline_name,
                pipeline_id=self.pipeline_id,
                metadata={
                    "dataset": self.dataset.name,
                    "ingestion_time": self.ingestion_time.isoformat()
                }
            )
        )
        self._audit_service.emit(event)

    def complete_pipeline(self) -> None:
        event = AuditEventFactory.create_pipeline_completed_event(
            PipelineCompletedAuditRequest(
                pipeline_name=self.pipeline_name,
                pipeline_id=self.pipeline_id,
                duration_ms=elapsed_milliseconds(self._started_at),
                metadata={
                    "dataset": self.dataset.name,
                    "ingestion_time": self.ingestion_time.isoformat()
                }
            )
        )
        self._audit_service.emit(event)

    def fail_pipeline(self, error: Exception) -> None:
        event = AuditEventFactory.create_pipeline_failed_event(
            PipelineFailedAuditRequest(
                pipeline_name=self.pipeline_name,
                pipeline_id=self.pipeline_id,
                duration_ms=elapsed_milliseconds(self._started_at),
                error=error,
                metadata={
                    "dataset": self.dataset.name,
                    "ingestion_time": self.ingestion_time.isoformat()
                }
            )
        )
        self._audit_service.emit(event)

    def start_task(self, step_id: str, step_name: str):
        start_event = AuditEventFactory.create_task_started_event(
            TaskStartedAuditRequest(
                pipeline_name=self.pipeline_name,
                pipeline_id=self.pipeline_id,
                task_name=step_name,
                task_id=step_id,
                task_attempt=1
            )
        )
        self._audit_service.emit(start_event)

    def complete_task(self, step_name: str, step_id: str, started_at: float | int):
        completed_event = AuditEventFactory.create_task_completed_event(
            TaskCompletedAuditRequest(
                pipeline_name=self.pipeline_name,
                pipeline_id=self.pipeline_id,
                task_name=step_name,
                task_id=step_id,
                task_attempt=1,
                duration_ms=elapsed_milliseconds(started_at)
            )
        )
        self._audit_service.emit(completed_event)

    def fail_task(self, step_name: str, step_id: str, error: Exception, started_at: float | int):
        failed_event = AuditEventFactory.create_task_failed_event(
            TaskFailedAuditRequest(
                pipeline_name=self.pipeline_name,
                pipeline_id=self.pipeline_id,
                task_name=step_name,
                task_id=step_id,
                task_attempt=1,
                duration_ms=elapsed_milliseconds(started_at),
                error=error
            )
        )
        self._audit_service.emit(failed_event)
