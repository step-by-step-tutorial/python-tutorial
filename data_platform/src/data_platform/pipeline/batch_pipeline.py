import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from data_platform.audit.audit_event_factory import AuditEventFactory
from data_platform.audit.audit_event_factory import PipelineCompletedAuditRequest
from data_platform.audit.audit_event_factory import PipelineFailedAuditRequest
from data_platform.audit.audit_event_factory import PipelineStartedAuditRequest
from data_platform.audit.audit_event_factory import TaskCompletedAuditRequest
from data_platform.audit.audit_event_factory import TaskFailedAuditRequest
from data_platform.audit.audit_event_factory import TaskStartedAuditRequest
from data_platform.audit.audit_service import AuditService
from data_platform.model import DataPopulator, Dataset, PipelineAnalyzer
from data_platform.util.log_utils import log_line
from data_platform.util.pipeline_utils import create_pipeline_id
from data_platform.util.time_utils import elapsed_milliseconds
from data_platform.util.time_utils import generate_ingestion_time

logger = logging.getLogger(__name__)


class BatchPipeline(ABC):
    pipeline_name: str

    def __init__(self, ds: Dataset, audit_service: AuditService | None = None) -> None:
        self.dataset = ds
        self.pipeline_id = create_pipeline_id()
        self.ingestion_time: datetime = generate_ingestion_time()
        self.audit_service = audit_service or AuditService(ds.audit)
        self.populators: tuple[DataPopulator, ...] = ()
        self.analyzers: tuple[PipelineAnalyzer, ...] = ()

    @abstractmethod
    def ingest_raw_data(self) -> Any:
        raise NotImplementedError

    @abstractmethod
    def store_raw_data(self, raw_data: Any) -> str:
        raise NotImplementedError

    @abstractmethod
    def clean(self, raw_relative_path: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    def store_cleaned_data(self, cleaned_data: Any) -> str:
        raise NotImplementedError

    @abstractmethod
    def enrich(self, cleaned_relative_path: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    def store_enriched_data(self, enriched_data: Any) -> str:
        raise NotImplementedError

    def populate_enriched_data(self, enriched_data_path: str) -> None:
        for populator in self.populators:
            populator.populate(enriched_data_path)

    @abstractmethod
    def show_dataframe(self, enriched_data_path: str) -> None:
        raise NotImplementedError

    def analyze_enriched_data(self, enriched_data_path: str) -> None:
        for analyzer in self.analyzers:
            analyzer.analyze(enriched_data_path)

    def before_run(self) -> None:
        return None

    def after_run(self) -> None:
        return None

    def run_task(self, task_name: str, task_callable):
        task_started_at = time.perf_counter()
        task_id = f"{self.pipeline_id}-{task_name}"
        self.audit_service.emit(
            AuditEventFactory.create_task_started_event(
                TaskStartedAuditRequest(
                    pipeline_name=self.pipeline_name,
                    pipeline_id=self.pipeline_id,
                    task_name=task_name,
                    task_id=task_id,
                    task_attempt=1,
                )
            )
        )

        try:
            result = task_callable()
        except Exception as error:
            self.audit_service.emit(
                AuditEventFactory.create_task_failed_event(
                    TaskFailedAuditRequest(
                        pipeline_name=self.pipeline_name,
                        pipeline_id=self.pipeline_id,
                        task_name=task_name,
                        task_id=task_id,
                        task_attempt=1,
                        duration_ms=elapsed_milliseconds(task_started_at),
                        error=error,
                    )
                )
            )
            raise
        else:
            self.audit_service.emit(
                AuditEventFactory.create_task_completed_event(
                    TaskCompletedAuditRequest(
                        pipeline_name=self.pipeline_name,
                        pipeline_id=self.pipeline_id,
                        task_name=task_name,
                        task_id=task_id,
                        task_attempt=1,
                        duration_ms=elapsed_milliseconds(task_started_at),
                    )
                )
            )
            return result

    def run(self) -> None:
        logger.info(
            f"Starting ETL pipeline {self.pipeline_name}/{self.pipeline_id} "
            f"with dataset {self.dataset.name} "
            f"at ingestion time {self.ingestion_time.isoformat()}"
        )
        pipeline_started_at = None
        try:
            pipeline_started_at = time.perf_counter()
            self.before_run()
            self.audit_service.emit(
                AuditEventFactory.create_pipeline_started_event(
                    PipelineStartedAuditRequest(
                        pipeline_name=self.pipeline_name,
                        pipeline_id=self.pipeline_id,
                        metadata={
                            "dataset": self.dataset.name,
                            "ingestion_time": self.ingestion_time.isoformat(),
                        },
                    )
                )
            )

            raw_data = self.run_task("ingest_raw_data", self.ingest_raw_data)
            log_line()

            raw_relative_path = self.run_task("store_raw_data", lambda: self.store_raw_data(raw_data))
            log_line()

            cleaned_data = self.run_task("clean", lambda: self.clean(raw_relative_path))
            log_line()

            cleaned_relative_path = self.run_task("store_cleaned_data", lambda: self.store_cleaned_data(cleaned_data))
            log_line()

            enriched_data = self.run_task("enrich", lambda: self.enrich(cleaned_relative_path))
            log_line()

            enriched_relative_path = self.run_task("store_enriched_data",
                                                   lambda: self.store_enriched_data(enriched_data))
            log_line()
            self.run_task("populate_enriched_data", lambda: self.populate_enriched_data(enriched_relative_path))
            log_line()
            self.run_task("show_dataframe", lambda: self.show_dataframe(enriched_relative_path))
            log_line()
            self.run_task("analyze_enriched_data", lambda: self.analyze_enriched_data(enriched_relative_path))
            log_line()
        except Exception as error:
            if pipeline_started_at is not None:
                self.audit_service.emit(
                    AuditEventFactory.create_pipeline_failed_event(
                        PipelineFailedAuditRequest(
                            pipeline_name=self.pipeline_name,
                            pipeline_id=self.pipeline_id,
                            duration_ms=elapsed_milliseconds(pipeline_started_at),
                            error=error,
                            metadata={
                                "dataset": self.dataset.name,
                                "ingestion_time": self.ingestion_time.isoformat(),
                            },
                        )
                    )
                )
            raise
        else:
            if pipeline_started_at is not None:
                self.audit_service.emit(
                    AuditEventFactory.create_pipeline_completed_event(
                        PipelineCompletedAuditRequest(
                            pipeline_name=self.pipeline_name,
                            pipeline_id=self.pipeline_id,
                            duration_ms=elapsed_milliseconds(pipeline_started_at),
                            metadata={
                                "dataset": self.dataset.name,
                                "ingestion_time": self.ingestion_time.isoformat(),
                            },
                        )
                    )
                )
                logger.info(
                    f"Finished ETL pipeline {self.pipeline_name}/{self.pipeline_id} "
                    f"with dataset {self.dataset.name} "
                    f"at ingestion time {self.ingestion_time.isoformat()}"
                )
        finally:
            self.after_run()
