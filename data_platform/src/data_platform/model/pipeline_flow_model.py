from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from data_platform.analyzer.analyzer_chain import AnalyzerChain
from data_platform.cleaner.cleaner_chain import CleanerChain
from data_platform.enricher.enricher_chain import EnricherChain
from data_platform.ingestion.dataset_ingestor import DatasetIngestor
from data_platform.repository.storage_repository import StorageRepository
from data_platform.validator.validator_chain import ValidatorChain


def _do_nothing(*args: Any, **kwargs: Any) -> None:
    return None


@dataclass(frozen=True)
class PipelineFlowModel:
    repository: StorageRepository | None = None
    backup_repository: StorageRepository | None = None
    ingestors: tuple[DatasetIngestor, ...] = ()
    cleaners: CleanerChain = CleanerChain()
    validators: ValidatorChain = ValidatorChain()
    enrichers: EnricherChain = EnricherChain()
    exposers: tuple[Any, ...] = ()
    analyzers: AnalyzerChain = AnalyzerChain()
    before_pipeline: Callable[..., Any] = _do_nothing
    after_pipeline: Callable[..., Any] = _do_nothing
    before_step: Callable[..., Any] = _do_nothing
    after_step: Callable[..., Any] = _do_nothing
