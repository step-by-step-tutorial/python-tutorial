import logging

import pandas as pd

from data_platform.config.data_lake_environment import StorageEnvironment
from data_platform.model import Dataset
from data_platform.pipeline.pipeline import Pipeline
from data_platform.util.path_utils import generate_relative_path

logger = logging.getLogger(__name__)


class DataPipeline(Pipeline):
    def __init__(self, dataset: Dataset) -> None:
        super().__init__(dataset)
        self.flow = dataset.flow

    def prepare(self) -> None:
        self.flow.before_pipeline(self)

    def ingest(self) -> str:
        raw_path = generate_relative_path(StorageEnvironment.RAW, self.ingestion_time, self.dataset.name)
        data = pd.concat(
            [ingestor.ingest() for ingestor in self.flow.ingestors],
            ignore_index=True,
        )
        return self.flow.repository.save(data, raw_path)

    def clean(self, path: str) -> str:
        cleaned_path = generate_relative_path(StorageEnvironment.CLEANED, self.ingestion_time, self.dataset.name)
        data = self.flow.repository.find(path)
        if self.flow.cleaner is not None:
            data = self.flow.cleaner.clean(data)
        return self.flow.repository.save(data, cleaned_path)

    def validate(self, path: str) -> str:
        validated_path = generate_relative_path(StorageEnvironment.VALIDATED, self.ingestion_time, self.dataset.name)
        invalid_path = generate_relative_path(StorageEnvironment.INVALID, self.ingestion_time, self.dataset.name)
        data = self.flow.repository.find(path)
        invalid_frames = []
        errors = []

        if self.flow.validator is not None:
            result = self.flow.validator.validate(data)
            data = result.valid
            if not result.invalid.empty:
                invalid_frames.append(result.invalid)
                errors.extend(result.errors)

        if invalid_frames:
            self.flow.repository.save(pd.concat(invalid_frames, ignore_index=True), invalid_path)
        if errors:
            logger.warning(f"Validation failed for dataset {self.dataset.name}: {errors}")

        return self.flow.repository.save(data, validated_path)

    def enrich(self, path: str) -> str:
        enriched_path = generate_relative_path(StorageEnvironment.ENRICHED, self.ingestion_time, self.dataset.name)
        data = self.flow.repository.find(path)
        if self.flow.enricher is not None:
            data = self.flow.enricher.enrich(data)
        return self.flow.repository.save(data, enriched_path)

    def expose(self, path: str) -> None:
        for exposer in self.flow.exposers:
            exposer.expose(self.flow.repository.find(path))

    def analyze(self, path: str) -> None:
        for analyzer in self.flow.analyzers:
            analyzer.analyze(self.flow.repository.find(path))

    def cleanup(self) -> None:
        self.flow.after_pipeline(self)
