from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


def _empty_hook(*_: Any) -> None:
    return None


@dataclass(frozen=True)
class PipelineFlow:
    storages: tuple[Any, ...] = ()
    ingestors: tuple[Any, ...] = ()
    cleaners: tuple[Any, ...] = ()
    enrichers: tuple[Any, ...] = ()
    exposers: tuple[Any, ...] = ()
    analyzers: tuple[Any, ...] = ()
    before_pipeline: Callable[..., Any] = _empty_hook
    after_pipeline: Callable[..., Any] = _empty_hook
    before_step: Callable[..., Any] = _empty_hook
    after_stage: Callable[..., Any] = _empty_hook

