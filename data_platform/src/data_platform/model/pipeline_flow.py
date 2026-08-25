from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from data_platform.analyzers import AnalyzerChain
from data_platform.cleaners import CleanerChain
from data_platform.enrichers import EnricherChain
from data_platform.model.dataset_ingestor import DatasetIngestor
from data_platform.persistence.storage_repository import StorageRepository
from data_platform.validators import ValidatorChain


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
