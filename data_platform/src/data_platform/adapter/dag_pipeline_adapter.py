from data_platform.pipeline.pipeline import Pipeline
from data_platform.util.path_utils import to_paths, to_object_storages


class DagPipelineAdapter:

    def __init__(self, pipeline: Pipeline) -> None:
        self._pipeline = pipeline

    def prepare(self) -> None:
        self._pipeline.start()
        self._pipeline.run_step("prepare", self._pipeline.prepare)

    def ingest(self) -> tuple[str, ...]:
        storage_objects = self._pipeline.run_step("ingest", self._pipeline.ingest)
        return to_paths(storage_objects)

    def clean(self, paths: tuple[str, ...]) -> tuple[str, ...]:
        storage_objects = self._pipeline.run_step("clean", lambda: self._pipeline.clean(to_object_storages(paths)))
        return to_paths(storage_objects)

    def enrich(self, paths: tuple[str, ...]) -> tuple[str, ...]:
        storage_objects = self._pipeline.run_step("enrich", lambda: self._pipeline.enrich(to_object_storages(paths)))
        return to_paths(storage_objects)

    def expose(self, paths: tuple[str, ...]) -> None:
        self._pipeline.run_step("expose", lambda: self._pipeline.expose(to_object_storages(paths)))

    def analyze(self, paths: tuple[str, ...]) -> None:
        self._pipeline.run_step("analyze", lambda: self._pipeline.analyze(to_object_storages(paths)))
        self._pipeline.complete()

    def cleanup(self) -> None:
        self._pipeline.run_step("cleanup", self._pipeline.cleanup)
