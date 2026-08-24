import time
from abc import ABC, abstractmethod
from typing import Any, Callable

from data_platform.audit.audit_event_factory import AuditEventFactory, PipelineCompletedAuditRequest, \
    PipelineFailedAuditRequest, PipelineStartedAuditRequest, TaskCompletedAuditRequest, TaskFailedAuditRequest, \
    TaskStartedAuditRequest
from data_platform.audit.audit_service import AuditService
from data_platform.config.data_lake_environment import DataLakeEnvironment
from data_platform.model import Artifact, Dataset
from data_platform.util.path_utils import generate_relative_path
from data_platform.util.pipeline_utils import create_pipeline_id
from data_platform.util.time_utils import elapsed_milliseconds, generate_ingestion_time


class BatchPipeline(ABC):

    def __init__(self, dataset: Dataset) -> None:
        self.dataset = dataset
        self.pipeline_name = dataset.name
        self.pipeline_id = create_pipeline_id()
        self.ingestion_time = generate_ingestion_time()
        self.path_prefix = generate_relative_path(DataLakeEnvironment.RAW, self.ingestion_time, self.dataset.name)
        self.started_at = None
        self.terminal = False
        self._audit_service = AuditService(dataset.audit)

    @abstractmethod
    def prepare(self) -> None:
        ...

    @abstractmethod
    def ingest(self) -> tuple[Artifact, ...]:
        ...

    @abstractmethod
    def clean(self, raw_artifact_paths: tuple[Artifact, ...]) -> tuple[Artifact, ...]:
        ...

    @abstractmethod
    def enrich(self, cleaned_artifact_paths: tuple[Artifact, ...]) -> tuple[Artifact, ...]:
        ...

    @abstractmethod
    def expose(self, enriched_artifact_paths: tuple[Artifact, ...]) -> None:
        ...

    @abstractmethod
    def analyze(self, enriched_artifact_paths: tuple[Artifact, ...]) -> None:
        ...

    @abstractmethod
    def cleanup(self) -> None:
        ...

    def start(self) -> None:
        if self.started_at is not None:
            return
        self.started_at = time.time()
        self._audit_service.emit(AuditEventFactory.create_pipeline_started_event(PipelineStartedAuditRequest(
            pipeline_name=self.pipeline_name, pipeline_id=self.pipeline_id,
            metadata={"dataset": self.dataset.name, "ingestion_time": self.ingestion_time.isoformat()},
        )))

    def complete(self) -> None:
        if self.terminal or self.started_at is None:
            return
        self.terminal = True
        self._audit_service.emit(AuditEventFactory.create_pipeline_completed_event(PipelineCompletedAuditRequest(
            pipeline_name=self.pipeline_name, pipeline_id=self.pipeline_id,
            duration_ms=elapsed_milliseconds(self.started_at),
            metadata={"dataset": self.dataset.name, "ingestion_time": self.ingestion_time.isoformat()},
        )))

    def fail(self, error: Exception) -> None:
        if self.terminal or self.started_at is None:
            return
        self.terminal = True
        self._audit_service.emit(AuditEventFactory.create_pipeline_failed_event(PipelineFailedAuditRequest(
            pipeline_name=self.pipeline_name, pipeline_id=self.pipeline_id,
            duration_ms=elapsed_milliseconds(self.started_at), error=error,
            metadata={"dataset": self.dataset.name, "ingestion_time": self.ingestion_time.isoformat()},
        )))

    def run_stage(self, stage_name: str, operation: Callable[[], Any]) -> Any:
        self.start()
        self.dataset.pipeline_steps.before_stage(stage_name)
        task_id = f"{self.pipeline_id}-{stage_name}"
        started_at = time.perf_counter()
        self._audit_service.emit(AuditEventFactory.create_task_started_event(TaskStartedAuditRequest(
            pipeline_name=self.pipeline_name, pipeline_id=self.pipeline_id, task_name=stage_name, task_id=task_id,
            task_attempt=1,
        )))
        try:
            result = operation()
        except Exception as error:
            self._audit_service.emit(AuditEventFactory.create_task_failed_event(TaskFailedAuditRequest(
                pipeline_name=self.pipeline_name, pipeline_id=self.pipeline_id, task_name=stage_name, task_id=task_id,
                task_attempt=1, duration_ms=elapsed_milliseconds(started_at), error=error,
            )))
            self.fail(error)
            raise
        self._audit_service.emit(AuditEventFactory.create_task_completed_event(TaskCompletedAuditRequest(
            pipeline_name=self.pipeline_name, pipeline_id=self.pipeline_id, task_name=stage_name, task_id=task_id,
            task_attempt=1, duration_ms=elapsed_milliseconds(started_at),
        )))
        self.dataset.pipeline_steps.after_stage(stage_name)
        return result

    def run(self) -> None:
        try:
            self.start()
            self.run_stage("prepare", self.prepare)
            raw_paths = self.run_stage("ingest", self.ingest)
            cleaned_paths = self.run_stage("clean", lambda: self.clean(raw_paths))
            enriched_paths = self.run_stage("enrich", lambda: self.enrich(cleaned_paths))
            self.run_stage("expose", lambda: self.expose(enriched_paths))
            self.run_stage("analyze", lambda: self.analyze(enriched_paths))
            self.complete()
        except Exception as error:
            self.fail(error)
            raise
        finally:
            self.run_stage("cleanup", self.cleanup)

