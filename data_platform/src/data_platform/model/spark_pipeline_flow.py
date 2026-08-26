from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from data_platform.model.dataset_ingestor import DatasetIngestor
from data_platform.repository.storage_repository import StorageRepository
from data_platform.spark_analyzers.analyzer_chain import SparkAnalyzerChain
from data_platform.spark_cleaners.cleaner_chain import SparkCleanerChain
from data_platform.spark_enrichers.enricher_chain import SparkEnricherChain
from data_platform.spark_validators.validator_chain import SparkValidatorChain


@dataclass(frozen=True)
class SparkPipelineFlow:
    repository: StorageRepository | None = None
    backup_repository: StorageRepository | None = None
    ingestors: tuple[DatasetIngestor, ...] = ()
    cleaners: SparkCleanerChain = SparkCleanerChain()
    validators: SparkValidatorChain = SparkValidatorChain()
    enrichers: SparkEnricherChain = SparkEnricherChain()
    exposers: tuple[Any, ...] = ()
    analyzers: SparkAnalyzerChain = SparkAnalyzerChain()
    before_pipeline: Callable[..., Any] = lambda *args, **kwargs: None
    after_pipeline: Callable[..., Any] = lambda *args, **kwargs: None
    before_step: Callable[..., Any] = lambda *args, **kwargs: None
    after_stage: Callable[..., Any] = lambda *args, **kwargs: None
