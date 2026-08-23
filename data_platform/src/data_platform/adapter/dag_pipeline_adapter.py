from data_platform.pipeline.batch_pipeline import BatchPipeline


class DagPipelineAdapter:
    def __init__(self, pipeline: BatchPipeline) -> None:
        self._pipeline = pipeline

    def prepare(self) -> None:
        self._pipeline.before_run()

    def ingest_raw_data(self) -> str:
        return self._pipeline.store_raw_data(self._pipeline.ingest_raw_data())

    def clean(self, raw_relative_path: str) -> str:
        return self._pipeline.store_cleaned_data(self._pipeline.clean(raw_relative_path))

    def enrich(self, cleaned_relative_path: str) -> str:
        return self._pipeline.store_enriched_data(self._pipeline.enrich(cleaned_relative_path))

    def populate_enriched_data(self, enriched_data_path: str) -> None:
        self._pipeline.populate_enriched_data(enriched_data_path)

    def analyze_enriched_data(self, enriched_data_path: str) -> None:
        self._pipeline.analyze_enriched_data(enriched_data_path)

    def clean_up(self) -> None:
        self._pipeline.after_run()
