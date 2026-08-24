from dataclasses import replace
from datetime import UTC, datetime

from data_platform.model import Artifact, AuditEndpoint, Dataset, PipelineSteps
from data_platform.pipeline.configured_pipeline import ConfiguredPipeline


def _factory(service):
    return lambda context: service


class _Lake:
    def __init__(self): self.data = {}
    def save(self, data, path): self.data[path] = data; return path
    def find(self, path): return self.data[path]


class _Transformer:
    def clean(self, value): return f"clean:{value}"
    def enrich(self, value): return f"enrich:{value}"


class _Source:
    def __init__(self, value): self.value = value
    def ingest(self): return self.value


def _ingestor_stage(artifact_name, value, lake):
    class Ingestor:
        name = artifact_name
        def ingest(self): return value
    stage = Ingestor()
    stage.storage_service = lake
    stage.storage_service_name = "storage"
    return stage


class _Consumer:
    def __init__(self): self.paths = []
    def expose(self, path): self.paths.append(path)
    def analyze(self, path): self.paths.append(path)


class _Transform:
    def __init__(self, name, operation, phase, lake): self.name, self.operation, self.phase, self.lake = name, operation, phase, lake; self.storage_service = lake; self.storage_service_name = "storage"
    def clean(self, value): return self.operation(value)
    def enrich(self, value): return self.operation(value)


class _Exposer:
    def __init__(self, consumer, lake): self.name = "expose"; self.consumer = consumer; self.storage_service = lake; self.storage_service_name = "storage"
    def expose(self, value): self.consumer.expose(value)


class _Analyzer:
    def __init__(self, consumer, lake): self.name = "analyze"; self.consumer = consumer; self.storage_service = lake; self.storage_service_name = "storage"
    def analyze(self, value): self.consumer.analyze(value)


def _dataset(lake, exposer, analyzer) -> Dataset:
    return Dataset(
        name="example",
        audit=AuditEndpoint("audit.database", "audit.kafka", "audit.datalake"),
        pipeline_steps=PipelineSteps(
            storages=(("storage", lake),),
            ingestors=(_ingestor_stage("first", "one", lake), _ingestor_stage("second", "two", lake)),
            cleaners=(
                _Transform("clean_one", _Transformer().clean, "cleaned", lake),
                _Transform("clean_two", _Transformer().clean, "cleaned", lake),
            ),
            enrichers=(
                _Transform("enrich_one", _Transformer().enrich, "enriched", lake),
                _Transform("enrich_two", _Transformer().enrich, "enriched", lake),
            ),
            exposers=(_Exposer(exposer, lake),),
            analyzers=(_Analyzer(analyzer, lake),),
        ),
    )


def test_configured_pipeline_executes_explicit_stages_without_merging_ingestors(mocker) -> None:
    lake, exposer, analyzer = _Lake(), _Consumer(), _Consumer()
    audit = mocker.Mock()
    mocker.patch("data_platform.pipeline.batch_pipeline.AuditService", return_value=audit)
    pipeline = ConfiguredPipeline(_dataset(lake, exposer, analyzer))
    pipeline.ingestion_time = datetime(2026, 1, 2, tzinfo=UTC)
    pipeline.run()

    raw_paths = tuple(path for path in lake.data if "/raw/" in path and "/cleaned/" not in path and "/enriched/" not in path)
    enriched_paths = tuple(path for path in lake.data if "/enriched/enrich_two/" in path)
    assert [path.rsplit("/", 1)[-1] for path in raw_paths] == ["first", "second"]
    assert all("/cleaned/clean_one/" in path for path in lake.data if "/cleaned/clean_one/" in path)
    assert all("/cleaned/clean_two/" in path for path in lake.data if "/cleaned/clean_two/" in path)
    assert all("/enriched/enrich_one/" in path for path in lake.data if "/enriched/enrich_one/" in path)
    assert enriched_paths
    assert lake.data[enriched_paths[0]] == "enrich:enrich:clean:clean:one"
    assert exposer.paths == ["enrich:enrich:clean:clean:one", "enrich:enrich:clean:clean:two"]
    assert analyzer.paths == exposer.paths
    assert audit.emit.call_count == 16



