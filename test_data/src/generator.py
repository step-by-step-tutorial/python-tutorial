"""Row generation.

The generator resolves the order columns must be produced in once, at construction
time, then reuses it for every row. A column may therefore be declared before the
column it depends on: ``country`` can be the last column of the CSV while the name,
phone, and address columns are all drawn from it.
"""


from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from random import Random
from typing import Mapping

from columns import ColumnGenerator, build_column_generator
from application_config import GeneratorConfig, load_config
from exceptions import DependencyError
from sources import SourceRepository
from writer import write_rows


@dataclass(frozen=True)
class GenerationResult:
    """What one generation run produced."""

    row_count: int
    output_path: Path


class CsvDataGenerator:
    """Turns a :class:`GeneratorConfig` into rows and a CSV file."""

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
        """Absolute path of the CSV this generator writes."""
        return self.project_root / self.config.output_file

    def iter_rows(self) -> Iterator[dict[str, str]]:
        """Yield rows one at a time, in the column order of the config."""
        headers = self.config.headers
        for row_index in range(self.config.row_count):
            values: dict[str, str] = {}
            for name in self._order:
                values[name] = self._generators[name].generate(values, row_index)
            yield {name: values[name] for name in headers}

    def generate_rows(self) -> list[dict[str, str]]:
        """Materialise every row. Prefer :meth:`iter_rows` for large datasets."""
        return list(self.iter_rows())

    def write_csv(self, rows: Iterable[Mapping[str, str]] | None = None) -> Path:
        """Write ``rows`` — or freshly generated ones — to the configured output."""
        write_rows(self.output_path, self.config.headers, self.iter_rows() if rows is None else rows)
        return self.output_path

    def generate(self) -> GenerationResult:
        """Generate and write the dataset, streaming rows straight to disk."""
        row_count = write_rows(self.output_path, self.config.headers, self.iter_rows())
        return GenerationResult(row_count=row_count, output_path=self.output_path)

    def _resolve_order(self) -> tuple[str, ...]:
        """Depth-first order that puts every column after the ones it depends on.

        Columns are visited in config order, so the sequence of random draws — and
        therefore the output of a seeded run — does not depend on how the
        dependencies happen to be laid out.
        """
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
    """Load a config file and generate its dataset in one call."""
    path = Path(config_path).resolve()
    config = load_config(path)
    return CsvDataGenerator(config=config, project_root=path.parent).generate()
