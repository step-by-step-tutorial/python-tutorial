

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from random import Random
from typing import Mapping

from application_config import GeneratorConfig, load_config
from columns import ColumnGenerator, build_column_generator
from database_repository import DatabaseRepository
from exceptions import ConfigurationError, DependencyError
from json_writer import write_json_rows
from sources import SourceRepository
from writer import write_rows


@dataclass(frozen=True)
class GenerationResult:

    row_count: int
    output_path: Path


class CsvDataGenerator:

    def __init__(
        self,
        config: GeneratorConfig,
        project_root: Path,
        sources: SourceRepository | None = None,
    ) -> None:
        self.config = config
        self.project_root = Path(project_root)
        self._sources = sources if sources is not None else SourceRepository(self.project_root)
        self._rng = Random(config.seed)
        self._generators: dict[str, ColumnGenerator] = {
            column.name: build_column_generator(column, self._sources, self._rng)
            for column in config.columns
        }
        self._order = self._resolve_order()

    @property
    def output_path(self) -> Path:
        return self.project_root / self.config.output_file

    def iter_rows(self) -> Iterator[dict[str, str]]:
        headers = self.config.headers
        for row_index in range(self.config.row_count):
            values: dict[str, str] = {}
            for name in self._order:
                values[name] = self._generators[name].generate(values, row_index)
            yield {name: values[name] for name in headers}

    def generate_rows(self) -> list[dict[str, str]]:
        return list(self.iter_rows())

    def write_csv(self, rows: Iterable[Mapping[str, str]] | None = None) -> Path:
        write_rows(self.output_path, self.config.headers, self.iter_rows() if rows is None else rows)
        return self.output_path

    def generate(self) -> GenerationResult:
        row_count = write_rows(self.output_path, self.config.headers, self.iter_rows())
        return GenerationResult(row_count=row_count, output_path=self.output_path)

    def _resolve_order(self) -> tuple[str, ...]:
        order: list[str] = []
        resolved: set[str] = set()

        def visit(name: str, pending: tuple[str, ...]) -> None:
            if name in resolved:
                return
            if name in pending:
                cycle = " -> ".join([*pending, name])
                raise DependencyError(f"Circular column dependency detected: {cycle}")

            generator = self._generators.get(name)
            if generator is None:
                dependent = pending[-1] if pending else name
                raise DependencyError(
                    f"Column {dependent!r} depends on unknown column {name!r}."
                )

            for dependency in generator.dependencies:
                visit(dependency, (*pending, name))

            resolved.add(name)
            order.append(name)

        for column in self.config.columns:
            visit(column.name, ())

        return tuple(order)


def generate_dataset(config_path: Path) -> GenerationResult:
    path = Path(config_path).resolve()
    config = load_config(path)
    if "kafka" in config.destinations:
        raise ConfigurationError("Kafka destination is not wired yet.")
    generator = CsvDataGenerator(config=config, project_root=path.parent)
    rows = generator.generate_rows()

    if "csv" in config.destinations:
        write_rows(generator.output_path, config.headers, rows)

    if "json" in config.destinations:
        json_path = generator.project_root / "output" / f"{generator.output_path.stem}.json"
        write_json_rows(json_path, rows)

    if "database" in config.destinations:
        DatabaseRepository().write_rows(
            table_name=generator.output_path.stem,
            headers=config.headers,
            rows=rows,
        )

    return GenerationResult(row_count=len(rows), output_path=generator.output_path)
