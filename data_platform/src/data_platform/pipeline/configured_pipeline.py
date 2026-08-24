from data_platform.model import Artifact, Dataset
from data_platform.pipeline.batch_pipeline import BatchPipeline
from data_platform.util.path_utils import artifact_name_from_path


class ConfiguredPipeline(BatchPipeline):

    def __init__(self, dataset: Dataset) -> None:
        super().__init__(dataset)
        self.definition = dataset.pipeline_steps

    def prepare(self) -> None:
        self.definition.before_pipeline(self)

    def ingest(self) -> tuple[Artifact, ...]:
        artifacts = []
        for ingestor in self.definition.ingestors:
            data = ingestor.ingest()
            path = ingestor.storage_service.save(
                data, f"{self.path_prefix}/{ingestor.name}"
            )
            artifacts.append(Artifact(ingestor.storage_service_name, path))
        return tuple(artifacts)

    def clean(self, raw_artifact_paths: tuple[Artifact, ...]) -> tuple[Artifact, ...]:
        paths = raw_artifact_paths
        for cleaner in self.definition.cleaners:
            outputs = []
            for artifact in paths:
                data = cleaner.storage_service.find(artifact.path)
                cleaned = cleaner.clean(data)
                path = cleaner.storage_service.save(
                    cleaned,
                    f"{self.path_prefix}/cleaned/{cleaner.name}/{artifact_name_from_path(artifact.path)}",
                )
                outputs.append(Artifact(cleaner.storage_service_name, path))
            paths = tuple(outputs)
        return paths

    def enrich(self, cleaned_artifact_paths: tuple[Artifact, ...]) -> tuple[Artifact, ...]:
        paths = cleaned_artifact_paths
        for enricher in self.definition.enrichers:
            outputs = []
            for artifact in paths:
                data = enricher.storage_service.find(artifact.path)
                enriched = enricher.enrich(data)
                path = enricher.storage_service.save(
                    enriched,
                    f"{self.path_prefix}/enriched/{enricher.name}/{artifact_name_from_path(artifact.path)}",
                )
                outputs.append(Artifact(enricher.storage_service_name, path))
            paths = tuple(outputs)
        return paths

    def expose(self, enriched_artifact_paths: tuple[Artifact, ...]) -> None:
        for exposer in self.definition.exposers:
            for artifact in enriched_artifact_paths:
                exposer.expose(exposer.storage_service.find(artifact.path))

    def analyze(self, enriched_artifact_paths: tuple[Artifact, ...]) -> None:
        for analyzer in self.definition.analyzers:
            for artifact in enriched_artifact_paths:
                analyzer.analyze(analyzer.storage_service.find(artifact.path))

    def cleanup(self) -> None:
        self.definition.after_pipeline(self)

