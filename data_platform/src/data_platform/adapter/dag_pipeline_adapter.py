from data_platform.model import Artifact
from data_platform.pipeline.batch_pipeline import BatchPipeline


class DagPipelineAdapter:

    def __init__(self, pipeline: BatchPipeline) -> None:
        self._pipeline = pipeline

    def prepare(self) -> None:
        self._pipeline.run_stage("prepare", self._pipeline.prepare)

    def ingest(self) -> tuple[str, ...]:
        return self._pipeline.run_stage("ingest", self._pipeline.ingest)

    def clean(self, raw_artifact_paths: tuple[Artifact, ...]) -> tuple[Artifact, ...]:
        return self._pipeline.run_stage("clean", lambda: self._pipeline.clean(raw_artifact_paths))

    def enrich(self, cleaned_artifact_paths: tuple[Artifact, ...]) -> tuple[Artifact, ...]:
        return self._pipeline.run_stage("enrich", lambda: self._pipeline.enrich(cleaned_artifact_paths))

    def expose(self, enriched_artifact_paths: tuple[Artifact, ...]) -> None:
        self._pipeline.run_stage("expose", lambda: self._pipeline.expose(enriched_artifact_paths))

    def analyze(self, enriched_artifact_paths: tuple[Artifact, ...]) -> None:
        self._pipeline.run_stage("analyze", lambda: self._pipeline.analyze(enriched_artifact_paths))
        self._pipeline.complete()

    def cleanup(self) -> None:
        self._pipeline.run_stage("cleanup", self._pipeline.cleanup)

