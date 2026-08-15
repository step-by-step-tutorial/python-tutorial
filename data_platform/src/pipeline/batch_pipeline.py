from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime

from audit.audit_service import AuditService
from dataset.definition import Dataset
from util.log_utils import log_line
from util.pipeline_utils import create_pipeline_id
from util.time_utils import generate_ingestion_time

logger = logging.getLogger(__name__)


class BatchPipeline(ABC):
    pipeline_name: str

    def __init__(self, ds: Dataset, audit_service: AuditService | None = None) -> None:
        self.dataset = ds
        self.pipeline_id = create_pipeline_id()
        self.ingestion_time: datetime = generate_ingestion_time()
        self.audit_service = audit_service or AuditService(ds.audit)

    @abstractmethod
    def store_raw_data(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def cleaning(self, raw_relative_path: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def enriching(self, cleaned_relative_path: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def populate_database(self, enriched_data_path: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def populate_datawarehouse(self, enriched_data_path: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def show_dataframe(self, enriched_data_path: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def analyze_primary(self, enriched_data_path: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def analyzing_via_datawarehouse(self) -> None:
        raise NotImplementedError

    def after_run(self) -> None:
        return None

    def _run_task(self, task_name: str, task_callable):
        task_id, started_at = self.audit_service.start_task(
            pipeline_name=self.pipeline_name,
            pipeline_id=self.pipeline_id,
            task_name=task_name,
            task_attempt=1,
        )

        try:
            result = task_callable()
        except Exception as error:
            self.audit_service.fail_task(
                pipeline_name=self.pipeline_name,
                pipeline_id=self.pipeline_id,
                task_name=task_name,
                task_id=task_id,
                task_attempt=1,
                started_at=started_at,
                error=error,
            )
            raise
        else:
            self.audit_service.complete_task(
                pipeline_name=self.pipeline_name,
                pipeline_id=self.pipeline_id,
                task_name=task_name,
                task_id=task_id,
                task_attempt=1,
                started_at=started_at,
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
            pipeline_started_at = self.audit_service.start_pipeline(
                pipeline_name=self.pipeline_name,
                pipeline_id=self.pipeline_id,
                metadata={
                    "dataset": self.dataset.name,
                    "ingestion_time": self.ingestion_time.isoformat(),
                },
            )

            raw_relative_path = self._run_task("store_raw_data", self.store_raw_data)
            log_line()
            cleaned_relative_path = self._run_task("cleaning", lambda: self.cleaning(raw_relative_path))
            log_line()
            enriched_relative_path = self._run_task("enriching", lambda: self.enriching(cleaned_relative_path))
            log_line()
            self._run_task("populate_database", lambda: self.populate_database(enriched_relative_path))
            log_line()
            self._run_task("populate_datawarehouse", lambda: self.populate_datawarehouse(enriched_relative_path))
            log_line()
            self._run_task("show_dataframe", lambda: self.show_dataframe(enriched_relative_path))
            log_line()
            self._run_task("analyze_primary", lambda: self.analyze_primary(enriched_relative_path))
            log_line()
            self._run_task("analyzing_via_datawarehouse", self.analyzing_via_datawarehouse)
            log_line()
        except Exception as error:
            if pipeline_started_at is not None:
                self.audit_service.fail_pipeline(
                    pipeline_name=self.pipeline_name,
                    pipeline_id=self.pipeline_id,
                    started_at=pipeline_started_at,
                    error=error,
                    metadata={
                        "dataset": self.dataset.name,
                        "ingestion_time": self.ingestion_time.isoformat(),
                    },
                )
            raise
        else:
            if pipeline_started_at is not None:
                self.audit_service.complete_pipeline(
                    pipeline_name=self.pipeline_name,
                    pipeline_id=self.pipeline_id,
                    started_at=pipeline_started_at,
                    metadata={
                        "dataset": self.dataset.name,
                        "ingestion_time": self.ingestion_time.isoformat(),
                    },
                )
                logger.info(
                    f"Finished ETL pipeline {self.pipeline_name}/{self.pipeline_id} "
                    f"with dataset {self.dataset.name} "
                    f"at ingestion time {self.ingestion_time.isoformat()}"
                )
        finally:
            self.after_run()
