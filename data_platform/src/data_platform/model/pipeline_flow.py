from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from data_platform.analyzers.analyzer_chain import AnalyzerChain
from data_platform.cleaners.cleaner_impl import CleanerChain
from data_platform.enrichers.enricher_impl import EnricherChain
from data_platform.model.dataset_ingestor import DatasetIngestor
from data_platform.repository.storage_repository import StorageRepository
from data_platform.validators.validator_chain import ValidatorChain


@dataclass(frozen=True)
class PipelineFlow:
    repository: StorageRepository | None = None
    ingestors: tuple[DatasetIngestor, ...] = ()
    cleaners: CleanerChain = CleanerChain()
    validators: ValidatorChain = ValidatorChain()
    enrichers: EnricherChain = EnricherChain()
    exposers: tuple[Any, ...] = ()
    analyzers: AnalyzerChain = AnalyzerChain()
    before_pipeline: Callable[..., Any] = lambda *args, **kwargs: None
    after_pipeline: Callable[..., Any] = lambda *args, **kwargs: None
    before_step: Callable[..., Any] = lambda *args, **kwargs: None
    after_stage: Callable[..., Any] = lambda *args, **kwargs: None
