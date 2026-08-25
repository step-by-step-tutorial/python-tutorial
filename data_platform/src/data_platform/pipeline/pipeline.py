import time
from abc import ABC, abstractmethod
from typing import Any, Callable

from data_platform.audit.audit_event_factory import AuditEventFactory, PipelineCompletedAuditRequest, \
    PipelineFailedAuditRequest, PipelineStartedAuditRequest, TaskCompletedAuditRequest, TaskFailedAuditRequest, \
    TaskStartedAuditRequest
from data_platform.audit.audit_service import AuditService
from data_platform.config.data_lake_environment import StorageEnvironment
from data_platform.model import Dataset, StorageObject
from data_platform.util.path_utils import generate_relative_path
from data_platform.util.pipeline_utils import create_pipeline_id
from data_platform.util.time_utils import elapsed_milliseconds, generate_ingestion_time


class Pipeline(ABC):

    def __init__(self, dataset: Dataset) -> None:
        self.dataset = dataset
        self.pipeline_name = dataset.name
        self.pipeline_id = create_pipeline_id()
        self.ingestion_time = generate_ingestion_time()
        self.storage_relative_path = generate_relative_path(StorageEnvironment.RAW, self.ingestion_time, self.dataset.name)
        self._started_at = None
        self._audit_service = AuditService(dataset.audit)

    @abstractmethod
    def prepare(self) -> None:
        ...

    @abstractmethod
    def ingest(self) -> tuple[StorageObject, ...]:
        ...

    @abstractmethod
    def clean(self, paths: tuple[StorageObject, ...]) -> tuple[StorageObject, ...]:
        ...

    @abstractmethod
    def enrich(self, paths: tuple[StorageObject, ...]) -> tuple[StorageObject, ...]:
        ...

    @abstractmethod
    def expose(self, paths: tuple[StorageObject, ...]) -> None:
        ...

    @abstractmethod
    def analyze(self, paths: tuple[StorageObject, ...]) -> None:
        ...

    @abstractmethod
    def cleanup(self) -> None:
        ...

    def start(self) -> None:
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

    def complete(self) -> None:
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

    def fail(self, error: Exception) -> None:
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

    def run_step(self, name: str, action: Callable[[], Any]) -> Any:
        self.dataset.flow.before_step(name)
        id = f"{self.pipeline_id}-{name}"
        started_at = time.perf_counter()
        start_event = AuditEventFactory.create_task_started_event(
            TaskStartedAuditRequest(
                pipeline_name=self.pipeline_name,
                pipeline_id=self.pipeline_id,
                task_name=name,
                task_id=id,
                task_attempt=1
            )
        )
        self._audit_service.emit(start_event)
        try:
            result = action()
        except Exception as error:
            failed_event = AuditEventFactory.create_task_failed_event(
                TaskFailedAuditRequest(
                    pipeline_name=self.pipeline_name,
                    pipeline_id=self.pipeline_id,
                    task_name=name,
                    task_id=id,
                    task_attempt=1,
                    duration_ms=elapsed_milliseconds(started_at),
                    error=error
                )
            )
            self._audit_service.emit(failed_event)
            self.fail(error)
            raise
        completed_event = AuditEventFactory.create_task_completed_event(
            TaskCompletedAuditRequest(
                pipeline_name=self.pipeline_name,
                pipeline_id=self.pipeline_id,
                task_name=name,
                task_id=id,
                task_attempt=1,
                duration_ms=elapsed_milliseconds(started_at)
            )
        )
        self._audit_service.emit(completed_event)
        self.dataset.flow.after_stage(name)
        return result

    def run(self) -> None:
        try:
            self.start()
            self.run_step("prepare", self.prepare)
            raw_paths = self.run_step("ingest", self.ingest)
            cleaned_paths = self.run_step("clean", lambda: self.clean(raw_paths))
            enriched_paths = self.run_step("enrich", lambda: self.enrich(cleaned_paths))
            self.run_step("expose", lambda: self.expose(enriched_paths))
            self.run_step("analyze", lambda: self.analyze(enriched_paths))
            self.complete()
        except Exception as error:
            self.fail(error)
            raise
        finally:
            self.run_step("cleanup", self.cleanup)
