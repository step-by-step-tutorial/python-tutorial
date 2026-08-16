from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from processor.base import DataProcessor


@dataclass(frozen=True)
class FileEndpoint:
    name: str = "file"
    file_name: str = ""
    file_path: str = ""
    file_format: str = "csv"
    encoding: str = "utf-8"

    def resolve_path(self, base_path: str | Path) -> Path:
        if self.file_path:
            return Path(self.file_path)

        if not self.file_name:
            raise ValueError("Cannot resolve file path because file_name is empty.")

        return Path(base_path) / self.file_name


@dataclass(frozen=True)
class DatabaseEndpoint:
    name: str = "database"
    table_name: str = ""
    preparing_sql_files: tuple[str, ...] = ()
    analytical_sql_files: tuple[str, ...] = ()


@dataclass(frozen=True)
class DataLakeEndpoint:
    name: str = "datalake"
    bucket_name: str = ""


@dataclass(frozen=True)
class DataWarehouseEndpoint:
    name: str = "datawarehouse"
    table_name: str = ""
    full_table_name: str = ""
    preparing_sql_files: Mapping[str, str] = field(default_factory=dict)
    analysis_sql_files: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class MessagingEndpoint:
    name: str = "messaging"
    topic: str = ""


@dataclass(frozen=True)
class Dataframe:
    schema: Any = None
    required_columns: frozenset[str] = frozenset()


@dataclass(frozen=True)
class Audit:
    topic: str = ""
    archive_enabled: bool = True


class Endpoint(Protocol):
    @property
    def name(self) -> str:
        ...


@dataclass(frozen=True, init=False)
class Dataset:
    name: str
    dataframe: Dataframe
    audit: Audit
    processor_factories: Mapping[str, Callable[[], DataProcessor]]
    sources: Mapping[str, Endpoint]
    destinations: Mapping[str, Endpoint]

    def __init__(
        self,
        name: str,
        dataframe: Dataframe | None = None,
        audit: Audit | None = None,
        processor_factories: Mapping[str, Callable[[], DataProcessor]] | None = None,
        sources: Mapping[str, Endpoint] | None = None,
        destinations: Mapping[str, Endpoint] | None = None,
    ) -> None:
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "dataframe", dataframe or Dataframe())
        object.__setattr__(self, "audit", audit or Audit())
        object.__setattr__(self, "processor_factories", dict(processor_factories or {}))
        object.__setattr__(self, "sources", dict(sources or {}))
        object.__setattr__(self, "destinations", dict(destinations or {}))

    def _lookup(self, mapping: Mapping[str, Endpoint], kind: str, name: str) -> Endpoint:
        try:
            return mapping[name]
        except KeyError as error:
            available = ", ".join(sorted(mapping)) or "<none>"
            raise KeyError(
                f"Unknown {kind} endpoint '{name}' for dataset '{self.name}'. Available: {available}"
            ) from error

    def get_source(self, name: str) -> Endpoint:
        return self._lookup(self.sources, "source", name)

    def get_destination(self, name: str) -> Endpoint:
        return self._lookup(self.destinations, "destination", name)

    def get_processor(self, name: str) -> DataProcessor:
        try:
            factory = self.processor_factories[name]
        except KeyError as error:
            available = ", ".join(sorted(self.processor_factories)) or "<none>"
            raise KeyError(
                f"Unknown processor '{name}' for dataset '{self.name}'. Available: {available}"
            ) from error

        return factory()

    @property
    def dataframe_schema(self) -> Any:
        return self.dataframe.schema

    @property
    def required_columns(self) -> frozenset[str]:
        return self.dataframe.required_columns
