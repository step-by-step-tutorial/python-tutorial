import logging

import pandas as pd

from data_platform.config.data_lake_environment import StorageEnvironment
from data_platform.model.dataset import Dataset
from data_platform.pipeline.pipeline import Pipeline
from data_platform.util.path_utils import generate_relative_path
from data_platform.validators.data_validator_utils import is_not_blank

logger = logging.getLogger(__name__)


class DataPipeline(Pipeline):
    def __init__(self, dataset: Dataset) -> None:
        super().__init__(dataset)
        self.flow = dataset.flow

    def prepare(self) -> None:
        self.flow.before_pipeline(self)

    def ingest(self) -> str:
        raw_path = generate_relative_path(StorageEnvironment.RAW, self.ingestion_time, self.dataset.name)
        data = pd.concat([ingestor.ingest() for ingestor in self.flow.ingestors], ignore_index=True)
        return self.flow.repository.write(data, raw_path)

    def clean(self, path: str) -> str:
        cleaned_path = generate_relative_path(StorageEnvironment.CLEANED, self.ingestion_time, self.dataset.name)
        data = self.flow.repository.read(path)
        data = self.flow.cleaners.clean(data)
        return self.flow.repository.write(data, cleaned_path)

    def validate(self, path: str) -> str:
        cleaned_data = self.flow.repository.read(path)
        assessment = self.flow.validators.validate(cleaned_data)

        accepted_path = generate_relative_path(StorageEnvironment.ACCEPTED, self.ingestion_time, self.dataset.name)
        rejected_path = generate_relative_path(StorageEnvironment.REJECTED, self.ingestion_time, self.dataset.name)
        accepted_data = assessment.accepted
        rejected_data = assessment.rejected
        errors = assessment.errors
        if is_not_blank(rejected_data):
            self.flow.repository.write(rejected_data, rejected_path)
            logger.error(f"Validation failed for dataset {self.dataset.name}: {errors}")

        return self.flow.repository.write(accepted_data, accepted_path)

    def enrich(self, path: str) -> str:
        enriched_path = generate_relative_path(StorageEnvironment.ENRICHED, self.ingestion_time, self.dataset.name)
        data = self.flow.repository.read(path)
        data = self.flow.enrichers.enrich(data)
        return self.flow.repository.write(data, enriched_path)

    def expose(self, path: str) -> None:
        data = self.flow.repository.read(path)
        for exposer in self.flow.exposers:
            exposer.expose(data)

    def analyze(self, path: str) -> None:
        results = self.flow.analyzers.analyze(self.flow.repository.read(path))
        for result in results or ():
            logger.info("Analysis result %s", result.name)

    def cleanup(self) -> None:
        if self.flow.after_pipeline is not None:
            self.flow.after_pipeline(self)
