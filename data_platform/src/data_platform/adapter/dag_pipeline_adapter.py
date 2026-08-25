from data_platform.pipeline.pipeline import Pipeline


class DagPipelineAdapter:

    def __init__(self, pipeline: Pipeline) -> None:
        self._pipeline = pipeline

    def prepare(self) -> None:
        self._pipeline.start()
        self._pipeline.run_step("prepare", self._pipeline.prepare)

    def ingest(self) -> str:
        return self._pipeline.run_step("ingest", self._pipeline.ingest)

    def clean(self, path: str) -> str:
        return self._pipeline.run_step("clean", lambda: self._pipeline.clean(path))

    def validate(self, path: str) -> str:
        return self._pipeline.run_step("validate", lambda: self._pipeline.validate(path))

    def enrich(self, path: str) -> str:
        return self._pipeline.run_step("enrich", lambda: self._pipeline.enrich(path))

    def expose(self, path: str) -> None:
        self._pipeline.run_step("expose", lambda: self._pipeline.expose(path))

    def analyze(self, path: str) -> None:
        self._pipeline.run_step("analyze", lambda: self._pipeline.analyze(path))
        self._pipeline.complete()

    def cleanup(self) -> None:
        self._pipeline.run_step("cleanup", self._pipeline.cleanup)
