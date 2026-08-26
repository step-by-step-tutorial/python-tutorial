from datetime import date

import pandas as pd
import pytest

from data_platform.analyzers.aggregate_model import AggregateSpecification
from data_platform.analyzers.analyzer_impl import GroupAggregateAnalyzer, RepositoryQueryAnalyzer
from data_platform.audit.audit_event import AuditEvent
from data_platform.cleaners.cleaner_impl import (
    BooleanColumnCleaner,
    CastColumnCleaner,
    CleanerChain,
    DropDuplicatesCleaner,
    FillMissingByColumnAverageCleaner,
    FillMissingByGroupAverageCleaner,
    NumericColumnCleaner,
    RenameColumnsCleaner,
    StripColumnCleaner,
    ToDatetimeCleaner,
)
from data_platform.enrichers.enricher_impl import (
    CalculateColumnEnricher,
    CopyColumnEnricher,
    DatetimePartEnricher,
    DivideColumnsEnricher,
    EnricherChain,
    HashColumnsEnricher,
    MultiplyColumnsEnricher,
    PercentageEnricher,
)
from data_platform.model.dataset import Dataset
from data_platform.model.dataframe_model import DataFrameModel
from data_platform.model.pipeline_flow import PipelineFlow
from data_platform.pipeline.data_pipeline import DataPipeline
from data_platform.repository.data_exposer import DataExposer
from data_platform.repository.storage_repository import StorageRepository
from data_platform.validators.data_validator_utils import (
    check_min_max,
    check_negative_days,
    is_blank,
    is_empty_collection,
    is_empty_text,
    is_none,
    is_not_blank,
    require_absent,
    require_blank,
    require_columns,
    require_iso_date,
    require_not_blank,
    require_or_default,
    require_or_raise_map,
    require_or_raise_tuple,
    require_xor,
    should_not_be_negative,
)
from data_platform.validators.validator_chain import ValidatorChain
from data_platform.validators.validator_impl import NonNegativeValidator, NotNullValidator, PositiveValidator


class MemoryRepository(StorageRepository):
    def __init__(self) -> None:
        self.paths: dict[str, pd.DataFrame] = {}

    def write(self, data: pd.DataFrame, path: str) -> str:
        self.paths[path] = data.copy()
        return path

    def read(self, path: str) -> pd.DataFrame:
        return self.paths[path].copy()


def test_cleaner_chain_converts_and_normalizes_dataframe() -> None:
    frame = pd.DataFrame({"number": [" 1,200 ", "3"], "flag": ["yes", "0"], "name": [" A ", "B"]})
    cleaned = CleanerChain((
        NumericColumnCleaner("number"),
        BooleanColumnCleaner("flag"),
        StripColumnCleaner("name"),
    )).clean(frame)

    assert cleaned.to_dict("records") == [
        {"number": 1200, "flag": True, "name": "A"},
        {"number": 3, "flag": False, "name": "B"},
    ]


def test_individual_cleaners_transform_expected_values() -> None:
    frame = pd.DataFrame({"a": [1, 1, 2], "b": [10.0, None, 30.0], "text": ["2026-01-01", "2026-01-02", "2026-01-02"]})
    deduplicated = DropDuplicatesCleaner("text").clean(frame)
    assert deduplicated[["a", "text"]].to_dict("records") == [
        {"a": 1, "text": "2026-01-01"},
        {"a": 1, "text": "2026-01-02"},
    ]
    assert pd.isna(deduplicated.iloc[1]["b"])
    cast_frame = pd.DataFrame({"text": ["1", "2", "2"]})
    assert CastColumnCleaner("text", "int").clean(cast_frame)["text"].tolist() == [1, 2, 2]
    renamed = RenameColumnsCleaner({"a": "group"}).clean(frame.copy())
    assert "group" in renamed and "a" not in renamed
    assert FillMissingByGroupAverageCleaner("a", "b").clean(frame.copy())["b"].tolist() == [10.0, 10.0, 30.0]
    assert FillMissingByColumnAverageCleaner("b").clean(frame.copy())["b"].tolist() == [10.0, 20.0, 30.0]
    assert ToDatetimeCleaner("text").clean(frame.copy())["text"].dt.year.tolist() == [2026, 2026, 2026]


def test_enrichers_add_expected_derived_values() -> None:
    frame = pd.DataFrame({"a": [2.0], "b": [3.0], "percent": [10.0], "when": pd.to_datetime(["2026-08-15"])})
    enriched = EnricherChain((
        MultiplyColumnsEnricher("a", "b", "product"),
        DivideColumnsEnricher("b", "a", "ratio"),
        PercentageEnricher("b", "percent", "discount"),
        CopyColumnEnricher("product", "copied", decimals=1),
        DatetimePartEnricher("when", "month", "month"),
        CalculateColumnEnricher("calculated", lambda row: row["a"] + row["b"]),
        HashColumnsEnricher(("a", "b"), "key"),
    )).enrich(frame)

    assert enriched.loc[0, ["product", "ratio", "discount", "copied", "month", "calculated"]].to_dict() == {
        "product": 6.0,
        "ratio": 1.5,
        "discount": 0.3,
        "copied": 6.0,
        "month": 8,
        "calculated": 5.0,
    }
    assert isinstance(enriched.loc[0, "key"], str) and len(enriched.loc[0, "key"]) == 64


def test_validators_return_accepted_rejected_rows_and_rules() -> None:
    frame = pd.DataFrame({"id": [1, None, 3], "amount": [2, -1, 0]})
    assessment = ValidatorChain((NotNullValidator("id"), PositiveValidator("amount"))).validate(frame)

    assert assessment.accepted.to_dict("records") == [{"id": 1.0, "amount": 2}]
    rejected = assessment.rejected
    assert rejected["amount"].tolist() == [-1, 0]
    assert pd.isna(rejected.iloc[0]["id"])
    assert rejected.iloc[1]["id"] == 3.0
    assert {violation.rule for violation in assessment.errors} == {"id_not_null", "amount_positive"}
    assert NonNegativeValidator("amount").validate(frame).accepted["amount"].tolist() == [2, 0]


def test_validator_utility_contracts() -> None:
    assert is_empty_collection([]) and is_empty_text("") and is_none(None)
    assert is_blank(None) and is_not_blank([1])
    assert require_blank([]) == []
    assert require_not_blank("value") == "value"
    assert require_or_default([], "fallback") == "fallback"
    assert require_or_raise_map({"a": 1}, "a") == 1
    assert require_or_raise_tuple(("a",), "a") == "a"
    assert require_absent(("a",), "b") is None
    assert check_min_max(1, 2) is None
    assert check_negative_days(date(2026, 1, 1), date(2026, 1, 3)) == 2
    assert require_iso_date("2026-01-02") == date(2026, 1, 2)
    assert require_xor("value", None) is None
    assert should_not_be_negative(0, 2) is None
    with pytest.raises(Exception):
        require_columns(pd.DataFrame({"id": [1]}), ("id", "missing"))
    with pytest.raises(Exception):
        require_xor("left", "right")


def test_analyzers_return_reports_with_data() -> None:
    frame = pd.DataFrame({"city": ["A", "A", "B"], "price": [10, 20, 5]})
    report = GroupAggregateAnalyzer(
        "average", AggregateSpecification("city", "price", "mean", "average_price")
    ).analyze(frame)
    assert report.name == "average"
    assert report.data.to_dict("records") == [
        {"city": "A", "average_price": 15.0},
        {"city": "B", "average_price": 5.0},
    ]
    query_report = RepositoryQueryAnalyzer("query", type("Repository", (), {"find_by_query": lambda self, _: (("ok",),)})()).analyze("select")
    assert query_report.data == (("ok",),)


def test_complete_pipeline_persists_each_stage_and_exposes_valid_data(mocker) -> None:
    source = pd.DataFrame({"id": [1, 2], "value": [10, -1]})
    repository = MemoryRepository()
    exposed: list[pd.DataFrame] = []
    analyzed: list[pd.DataFrame] = []
    lifecycle: list[str] = []

    class Ingestor:
        name = "memory"

        def ingest(self) -> pd.DataFrame:
            return source.copy()

    class Analyzer:
        name = "summary"

        def analyze(self, frame: pd.DataFrame):
            analyzed.append(frame.copy())
            return type("Report", (), {"name": self.name, "data": frame})()

    mocker.patch("data_platform.pipeline.pipeline.AuditService", return_value=mocker.Mock())
    dataset = Dataset(
        name="example",
        audit=mocker.Mock(),
        dataframe=DataFrameModel(required_columns=frozenset({"id", "value"})),
        flow=PipelineFlow(
            repository=repository,
            ingestors=(Ingestor(),),
            cleaners=CleanerChain(),
            validators=ValidatorChain((PositiveValidator("value"),)),
            enrichers=EnricherChain((CopyColumnEnricher("value", "enriched_value"),)),
            exposers=(DataExposer((lambda frame: exposed.append(frame.copy()),)),),
            analyzers=type("AnalyzerChain", (), {"analyze": lambda self, frame: (Analyzer().analyze(frame),)})(),
            before_pipeline=lambda _: lifecycle.append("before_pipeline"),
            after_pipeline=lambda _: lifecycle.append("after_pipeline"),
            before_step=lambda step: lifecycle.append(f"before:{step}"),
            after_stage=lambda step: lifecycle.append(f"after:{step}"),
        ),
    )

    DataPipeline(dataset).run()

    assert len(repository.paths) == 6
    report_paths = tuple(path for path in repository.paths if path.startswith("reports/example/"))
    assert len(report_paths) == 1
    assert report_paths[0].endswith("/summary")
    assert {"id", "value", "enriched_value"} == set(exposed[0].columns)
    assert exposed[0]["id"].tolist() == [1]
    assert analyzed[0]["enriched_value"].tolist() == [10]
    assert "before_pipeline" in lifecycle
    assert "after_pipeline" in lifecycle
