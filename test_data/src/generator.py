from collections.abc import Iterable, Iterator
from pathlib import Path
from random import Random
from typing import Mapping

import env_config
from application_config import GeneratorConfig, load_config
from columns import ColumnGenerator, build_column_generator
from writer_registry import WRITER_REGISTRY
from exceptions import DependencyError
from sources import SourceRepository
from csv_utils import write_csv


class DataGenerator:

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
        return env_config.OUTPUT_DIR / self.config.output_file

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
        write_csv(self.output_path, self.config.headers, self.iter_rows() if rows is None else rows)
        return self.output_path

    def generate(self) -> None:
        rows = self.generate_rows()
        write_csv(self.output_path, self.config.headers, rows)

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


def generate_dataset(config_path: Path) -> None:
    path = Path(config_path).resolve()
    config = load_config(path.name)
    generator = DataGenerator(config=config, project_root=path.parent.parent)
    rows = generator.generate_rows()
    WRITER_REGISTRY.write_all(rows, config)
