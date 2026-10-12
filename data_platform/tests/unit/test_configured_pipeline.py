from dataclasses import replace
from datetime import UTC, datetime

import pandas as pd

from data_platform.model.endpoint_model import AuditEndpointModel
from data_platform.model.dataset_model import DatasetModel
from data_platform.model.pipeline_flow_model import PipelineFlowModel
from data_platform.model.assessment_model import AssessmentModel
from data_platform.model.violation_model import ViolationModel
from data_platform.cleaner.cleaner_chain import CleanerChain
from data_platform.enricher.enricher_chain import EnricherChain
from data_platform.validator.validator_chain import ValidatorChain
from data_platform.pipeline.inmemory_pipeline import InmemoryPipeline
from data_platform.model.report_model import ReportModel


def _factory(service):
    return lambda context: service


class _Lake:
    def __init__(self): self.data = {}
    def write(self, data, path): self.data[path] = data; return path
    def read(self, path): return self.data[path]


class _Transformer:
    def clean(self, value): return f"clean:{value}"
    def enrich(self, value): return f"enrich:{value}"


class _Validator:
    def validate(self, frame):
        return AssessmentModel(
            accepted=frame.iloc[1:],
            rejected=frame.iloc[:1],
            errors=(ViolationModel("first_row", "The first row is invalid"),),
        )


class _Source:
    def __init__(self, value): self.value = value
    def ingest(self): return self.value


def _ingestor_stage(storage_object_name, value, lake):
    class Ingestor:
        name = storage_object_name
        def ingest(self): return pd.DataFrame({"value": [value]})
    stage = Ingestor()
    stage.storage_service = lake
    stage.storage_service_name = "storage"
    return stage


class _Consumer:
    def __init__(self): self.paths = []
    def expose(self, path): self.paths.append(path)
    def analyze(self, path): self.paths.append(path)


class _Transform:
    def __init__(self, name, clean_operation, enrich_operation, lake): self.name, self.clean_operation, self.enrich_operation, self.lake = name, clean_operation, enrich_operation, lake; self.storage_service = lake; self.storage_service_name = "storage"
    def clean(self, value): return self.clean_operation(value)
    def enrich(self, value): return self.enrich_operation(value)


class _Exposer:
    def __init__(self, consumer, lake): self.name = "expose"; self.consumer = consumer; self.storage_service = lake; self.storage_service_name = "storage"
    def expose(self, value): self.consumer.expose(value)


class _Analyzer:
    def __init__(self, consumer, lake): self.name = "analyze"; self.consumer = consumer; self.storage_service = lake; self.storage_service_name = "storage"
    def analyze(self, value):
        self.consumer.analyze(value)
        return (ReportModel("summary", pd.DataFrame({"value": [1]})),)


def _dataset(lake, exposer, analyzer) -> DatasetModel:
    return DatasetModel(
        name="example",
        audit=AuditEndpointModel("audit.database", "audit.kafka", "audit.datalake"),
        flow=PipelineFlowModel(
            repository=lake,
            ingestors=(_ingestor_stage("first", "one", lake), _ingestor_stage("second", "two", lake)),
            cleaners=CleanerChain((
                _Transform("transform_one", _Transformer().clean, _Transformer().enrich, lake),
                _Transform("transform_two", _Transformer().clean, _Transformer().enrich, lake),
            )),
            enrichers=EnricherChain((
                _Transform("transform_one", _Transformer().clean, _Transformer().enrich, lake),
                _Transform("transform_two", _Transformer().clean, _Transformer().enrich, lake),
            )),
            exposers=(_Exposer(exposer, lake),),
            analyzers=_Analyzer(analyzer, lake),
        ),
    )


def test_configured_pipeline_executes_explicit_stages_without_merging_ingestors(mocker) -> None:
    lake, exposer, analyzer = _Lake(), _Consumer(), _Consumer()
    audit = mocker.Mock()
    mocker.patch("data_platform.pipeline.pipeline.AuditService", return_value=audit)
    pipeline = InmemoryPipeline(_dataset(lake, exposer, analyzer))
    pipeline.ingestion_time = datetime(2026, 1, 2, tzinfo=UTC)
    pipeline.run()

    raw_paths = tuple(path for path in lake.data if path.startswith("raw/") and "/cleaned/" not in path and "/enriched/" not in path)
    enriched_paths = tuple(path for path in lake.data if path.startswith("enriched/"))
    assert len(raw_paths) == 1
    assert any(path.startswith("cleaned/") for path in lake.data)
    assert not any("/step_" in path for path in lake.data)
    assert enriched_paths
    assert isinstance(lake.data[enriched_paths[0]], str)
    assert len(exposer.paths) == 1
    assert analyzer.paths == exposer.paths
    assert audit.emit.call_count == 18


def test_pipeline_can_complete_when_created_in_a_later_airflow_task(mocker) -> None:
    audit = mocker.Mock()
    mocker.patch("data_platform.pipeline.pipeline.AuditService", return_value=audit)
    pipeline = InmemoryPipeline(_dataset(_Lake(), _Consumer(), _Consumer()))

    pipeline.complete_pipeline()

    event = audit.emit.call_args.args[0]
    assert event.duration_ms >= 0


def test_configured_pipeline_persists_invalid_rows_and_logs_validation_errors(mocker, caplog) -> None:
    lake, exposer, analyzer = _Lake(), _Consumer(), _Consumer()
    mocker.patch("data_platform.pipeline.pipeline.AuditService", return_value=mocker.Mock())
    dataset = _dataset(lake, exposer, analyzer)
    dataset = replace(dataset, flow=replace(dataset.flow, validators=ValidatorChain((_Validator(),))))
    pipeline = InmemoryPipeline(dataset)
    lake.data["raw/input"] = pd.DataFrame({"value": ["invalid", "valid"]})

    validated_path = pipeline.validate("raw/input")

    invalid_paths = tuple(path for path in lake.data if path.startswith("invalid/"))
    assert len(invalid_paths) == 1
    assert lake.data[invalid_paths[0]]["value"].tolist() == ["invalid"]
    assert lake.data[validated_path]["value"].tolist() == ["valid"]
    assert "first_row" in caplog.text
    assert "The first row is invalid" in caplog.text
