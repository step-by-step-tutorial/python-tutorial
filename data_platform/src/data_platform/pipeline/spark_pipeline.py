import logging

from data_platform.config.data_lake_environment import StorageEnvironment
from data_platform.model.dataset import Dataset
from data_platform.pipeline.pipeline import Pipeline
from data_platform.util.path_utils import generate_relative_path, join_path

logger = logging.getLogger(__name__)


class SparkPipeline(Pipeline):
    def __init__(self, dataset: Dataset) -> None:
        super().__init__(dataset)
        self.flow = dataset.flow
        self._repository = self.flow.repository
        self._backup_repository = self.flow.backup_repository
        self._ingestors = self.flow.ingestors
        self._exposers = self.flow.exposers

    def prepare(self) -> None:
        self.flow.before_pipeline(self)

    def ingest(self) -> str:
        path = generate_relative_path(StorageEnvironment.RAW, self.ingestion_time, self.dataset.name)
        dataframes = [ingestor.ingest() for ingestor in self._ingestors]
        if not dataframes:
            raise ValueError(f"Dataset '{self.dataset.name}' has no Spark ingestors configured.")
        data = dataframes[0]
        for dataframe in dataframes[1:]:
            data = data.unionByName(dataframe, allowMissingColumns=True)
        logger.info("Ingested Spark dataset: dataset=%s rows=%s columns=%s path=%s", self.dataset.name, data.count(),
                    len(data.columns), path)
        return self._write(data, path, "raw")

    def clean(self, path: str) -> str:
        output_path = generate_relative_path(StorageEnvironment.CLEANED, self.ingestion_time, self.dataset.name)
        data = self.flow.cleaners.clean(self._repository.read(path))
        logger.info("Cleaned Spark dataset: dataset=%s rows=%s path=%s", self.dataset.name, data.count(), output_path)
        return self._write(data, output_path, "cleaned")

    def validate(self, path: str) -> str:
        assessment = self.flow.validators.validate(self._repository.read(path))
        accepted_path = generate_relative_path(StorageEnvironment.ACCEPTED, self.ingestion_time, self.dataset.name)
        rejected_path = generate_relative_path(StorageEnvironment.REJECTED, self.ingestion_time, self.dataset.name)
        if not assessment.rejected.isEmpty():
            self._repository.write(assessment.rejected, rejected_path)
            logger.warning("Spark validation rejected rows: dataset=%s rows=%s errors=%s", self.dataset.name,
                           assessment.rejected.count(), len(assessment.errors))
        return self._write(assessment.accepted, accepted_path, "accepted")

    def enrich(self, path: str) -> str:
        output_path = generate_relative_path(StorageEnvironment.ENRICHED, self.ingestion_time, self.dataset.name)
        data = self.flow.enrichers.enrich(self._repository.read(path))
        logger.info("Enriched Spark dataset: dataset=%s rows=%s path=%s", self.dataset.name, data.count(), output_path)
        return self._write(data, output_path, "enriched")

    def expose(self, path: str) -> None:
        data = self._repository.read(path)
        for exposer in self._exposers:
            exposer.expose(data)

    def analyze(self, path: str) -> None:
        reports_path = generate_relative_path(StorageEnvironment.REPORTS, self.ingestion_time, self.dataset.name)
        for result in self.flow.analyzers.analyze(self._repository.read(path)):
            report_path = join_path(reports_path, result.name)
            self._repository.write(result.data, report_path)
            logger.info("Spark analyzer report persisted: dataset=%s report=%s path=%s rows=%s", self.dataset.name,
                        result.name, report_path, result.data.count())

    def cleanup(self) -> None:
        self.flow.after_pipeline(self)

    def _write(self, data, path: str, stage: str) -> str:
        result = self._repository.write(data, path)
        if self._backup_repository is not None:
            self._backup_repository.write(data, path)
            logger.info("Backed up Spark dataset stage: dataset=%s stage=%s path=%s", self.dataset.name, stage, path)
        return result
