from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from data_platform.persistence.storage_repository import StorageRepository
from data_platform.model.cleaner import Cleaner
from data_platform.model.dataset_ingestor import DatasetIngestor
from data_platform.model.enricher import Enricher
from data_platform.model.validator import Validator


def _empty_hook(*_: Any) -> None:
    return None


@dataclass(frozen=True)
class PipelineFlow:
    repository: StorageRepository | None = None
    ingestors: tuple[DatasetIngestor, ...] = ()
    cleaner: Cleaner | None = None
    validator: Validator | None = None
    enricher: Enricher | None = None
    exposers: tuple[Any, ...] = ()
    analyzers: tuple[Any, ...] = ()
    before_pipeline: Callable[..., Any] = _empty_hook
    after_pipeline: Callable[..., Any] = _empty_hook
    before_step: Callable[..., Any] = _empty_hook
    after_stage: Callable[..., Any] = _empty_hook
