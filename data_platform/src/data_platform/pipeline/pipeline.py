import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Callable
from uuid import uuid4

from data_platform.audit.audit_service import AuditService
from data_platform.config.storage_environment import StorageEnvironment
from data_platform.model.audit_event_model import AuditEventModel
from data_platform.model.audit_request_model import (
    PipelineCompletedAuditRequestModel,
    PipelineFailedAuditRequestModel,
    PipelineStartedAuditRequestModel,
    TaskCompletedAuditRequestModel,
    TaskFailedAuditRequestModel,
    TaskStartedAuditRequestModel,
)
from data_platform.model.dataset_model import DatasetModel
from data_platform.util.path_utils import generate_relative_path, join_path
from data_platform.util.time_utils import elapsed_milliseconds, generate_ingestion_time

logger = logging.getLogger(__name__)


class Pipeline(ABC):

    def __init__(self, dataset: DatasetModel) -> None:
        self.dataset = dataset
        self.flow = dataset.flow
        self.pipeline_name = dataset.name
        self.pipeline_id = str(uuid4())
        self.ingestion_time = generate_ingestion_time()
        # DAG task processes are isolated, so a later task may not see prepare()'s timestamp.
        self._started_at = time.perf_counter()
        self._audit_service = AuditService(dataset.audit)

    @abstractmethod
    def combine(self, dataframes: list[Any]) -> Any:
        ...

    @abstractmethod
    def count(self, dataframe: Any) -> int:
        ...

    @abstractmethod
    def is_empty(self, dataframe: Any) -> bool:
        ...

    @abstractmethod
    def to_dataframe(self, data: Any) -> Any:
        ...

    def prepare(self) -> None:
        logger.info("Preparing dataset: dataset=%s pipeline_id=%s", self.dataset.name, self.pipeline_id)
        self.flow.before_pipeline(self)

    def ingest(self) -> str:
        dataframes = [ingestor.ingest() for ingestor in self.flow.ingestors]
        if not dataframes:
            raise ValueError(f"Dataset '{self.dataset.name}' has no ingestors configured.")
        data = self.combine(dataframes)
        raw_path = self.stage_path(StorageEnvironment.RAW)
        logger.info("Ingested dataset: dataset=%s rows=%s columns=%s path=%s", self.dataset.name, self.count(data),
                    len(data.columns), raw_path)
        return self.write(data, raw_path, "raw")

    def clean(self, path: str) -> str:
        data = self.flow.cleaners.clean(self.flow.repository.read(path))
        cleaned_path = self.stage_path(StorageEnvironment.CLEANED)
        logger.info("Cleaned dataset: dataset=%s rows=%s path=%s", self.dataset.name, self.count(data), cleaned_path)
        return self.write(data, cleaned_path, "cleaned")

    def validate(self, path: str) -> str:
        assessment = self.flow.validators.validate(self.flow.repository.read(path))
        logger.info("Validated dataset: dataset=%s accepted_rows=%s rejected_rows=%s error_count=%s",
                    self.dataset.name, self.count(assessment.accepted), self.count(assessment.rejected),
                    len(assessment.errors))
        if not self.is_empty(assessment.rejected):
            self.flow.repository.write(assessment.rejected, self.stage_path(StorageEnvironment.REJECTED))
            logger.warning("Validation rejected rows: dataset=%s errors=%s", self.dataset.name, assessment.errors)
        return self.write(assessment.accepted, self.stage_path(StorageEnvironment.ACCEPTED), "accepted")

    def enrich(self, path: str) -> str:
        data = self.flow.enrichers.enrich(self.flow.repository.read(path))
        enriched_path = self.stage_path(StorageEnvironment.ENRICHED)
        logger.info("Enriched dataset: dataset=%s rows=%s path=%s", self.dataset.name, self.count(data), enriched_path)
        return self.write(data, enriched_path, "enriched")

    def expose(self, path: str) -> None:
        data = self.flow.repository.read(path)
        for exposer in self.flow.exposers:
            exposer.expose(data)

    def analyze(self, path: str) -> None:
        reports = self.flow.analyzers.analyze(self.flow.repository.read(path))
        logger.info("Analyzer completed: dataset=%s report_count=%s", self.dataset.name, len(reports))
        for report in reports:
            report_path = join_path(self.stage_path(StorageEnvironment.REPORTS), report.name)
            report_data = self.to_dataframe(report.data)
            self.flow.repository.write(report_data, report_path)
            logger.info("Analyzer report persisted: dataset=%s report=%s path=%s rows=%s", self.dataset.name,
                        report.name, report_path, self.count(report_data))

    def cleanup(self) -> None:
        self.flow.after_pipeline(self)

    def stage_path(self, environment: StorageEnvironment) -> str:
        return generate_relative_path(environment, self.ingestion_time, self.dataset.name)

    def write(self, data: Any, path: str, stage: str) -> str:
        result = self.flow.repository.write(data, path)
        if self.flow.backup_repository is not None:
            self.flow.backup_repository.write(data, path)
            logger.info("Backed up dataset stage: dataset=%s stage=%s path=%s", self.dataset.name, stage, path)
        return result

    def run_step(self, step_name: str, action: Callable[[], Any]) -> Any:
        self.flow.before_step(step_name)
        step_id = f"{self.pipeline_id}-{step_name}"
        started_at = time.perf_counter()
        logger.info("Pipeline step started: dataset=%s pipeline_id=%s step=%s", self.pipeline_name, self.pipeline_id,
                    step_name)
        self.start_task(step_id, step_name)
        try:
            result = action()
        except Exception as error:
            logger.error("Pipeline step failed: dataset=%s pipeline_id=%s step=%s error=%s", self.pipeline_name,
                         self.pipeline_id, step_name, error)
            self.fail_task(step_name, step_id, error, started_at)
            raise
        self.complete_task(step_name, step_id, started_at)
        self.flow.after_step(step_name)
        logger.info("Pipeline step completed: dataset=%s pipeline_id=%s step=%s duration_ms=%s", self.pipeline_name,
                    self.pipeline_id, step_name, elapsed_milliseconds(started_at))
        return result

    def run(self) -> None:
        try:
            self.start_pipeline()
            self.run_step("prepare", self.prepare)
            raw_path = self.run_step("ingest", self.ingest)
            cleaned_path = self.run_step("clean", lambda: self.clean(raw_path))
            validated_path = self.run_step("validate", lambda: self.validate(cleaned_path))
            enriched_path = self.run_step("enrich", lambda: self.enrich(validated_path))
            self.run_step("expose", lambda: self.expose(enriched_path))
            self.run_step("analyze", lambda: self.analyze(enriched_path))
            self.complete_pipeline()
        except Exception as error:
            self.fail_pipeline(error)
            raise
        finally:
            self.run_step("cleanup", self.cleanup)

    def _pipeline_metadata(self) -> dict[str, str]:
        return {"dataset": self.dataset.name, "ingestion_time": self.ingestion_time.isoformat()}

    def start_pipeline(self) -> None:
        self._started_at = time.perf_counter()
        logger.info("Pipeline started: dataset=%s pipeline_id=%s ingestion_time=%s", self.pipeline_name,
                    self.pipeline_id, self.ingestion_time.isoformat())
        self._audit_service.emit(AuditEventModel.from_pipeline_started(
            PipelineStartedAuditRequestModel(
                pipeline_name=self.pipeline_name,
                pipeline_id=self.pipeline_id,
                metadata=self._pipeline_metadata(),
            )
        ))

    def complete_pipeline(self) -> None:
        duration_ms = elapsed_milliseconds(self._started_at)
        logger.info("Pipeline completed: dataset=%s pipeline_id=%s duration_ms=%s", self.pipeline_name,
                    self.pipeline_id, duration_ms)
        self._audit_service.emit(AuditEventModel.from_pipeline_completed(
            PipelineCompletedAuditRequestModel(
                pipeline_name=self.pipeline_name,
                pipeline_id=self.pipeline_id,
                duration_ms=duration_ms,
                metadata=self._pipeline_metadata(),
            )
        ))

    def fail_pipeline(self, error: Exception) -> None:
        duration_ms = elapsed_milliseconds(self._started_at)
        logger.error("Pipeline failed: dataset=%s pipeline_id=%s duration_ms=%s error=%s", self.pipeline_name,
                     self.pipeline_id, duration_ms, error)
        self._audit_service.emit(AuditEventModel.from_pipeline_failed(
            PipelineFailedAuditRequestModel(
                pipeline_name=self.pipeline_name,
                pipeline_id=self.pipeline_id,
                duration_ms=duration_ms,
                error=error,
                metadata=self._pipeline_metadata(),
            )
        ))

    def start_task(self, step_id: str, step_name: str) -> None:
        self._audit_service.emit(AuditEventModel.from_task_started(
            TaskStartedAuditRequestModel(
                pipeline_name=self.pipeline_name,
                pipeline_id=self.pipeline_id,
                task_name=step_name,
                task_id=step_id,
                task_attempt=1,
            )
        ))

    def complete_task(self, step_name: str, step_id: str, started_at: float) -> None:
        self._audit_service.emit(AuditEventModel.from_task_completed(
            TaskCompletedAuditRequestModel(
                pipeline_name=self.pipeline_name,
                pipeline_id=self.pipeline_id,
                task_name=step_name,
                task_id=step_id,
                task_attempt=1,
                duration_ms=elapsed_milliseconds(started_at),
            )
        ))

    def fail_task(self, step_name: str, step_id: str, error: Exception, started_at: float) -> None:
        self._audit_service.emit(AuditEventModel.from_task_failed(
            TaskFailedAuditRequestModel(
                pipeline_name=self.pipeline_name,
                pipeline_id=self.pipeline_id,
                task_name=step_name,
                task_id=step_id,
                task_attempt=1,
                duration_ms=elapsed_milliseconds(started_at),
                error=error,
            )
        ))
