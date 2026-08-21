from collections.abc import Iterator
from random import Random

from columns import ColumnGenerator, get_column_generator
from config_manager import load_config
from datasets import Dataset
from sources import SourceRepository
from writer_registry import writer_registry


class DataGenerator:

    def __init__(
            self,
            config_name: str,
            sources: SourceRepository | None = None,
    ) -> None:
        self.config_name = config_name
        self.config = load_config(config_name)
        self._sources = sources if sources is not None else SourceRepository()
        self._rng = Random(self.config.seed)
        self._generators: dict[str, ColumnGenerator] = {
            column.name: get_column_generator(column, self._sources, self._rng)
            for column in self.config.columns
        }
        self._order = self._resolve_order()

    def iter_rows(self) -> Iterator[dict[str, str]]:
        headers = self.config.headers
        for row_index in range(self.config.row_count):
            values: dict[str, str] = {}
            for name in self._order:
                values[name] = self._generators[name].generate(values, row_index)
            yield {name: values[name] for name in headers}

    def generate_dataset(self) -> Dataset:
        rows = list(self.iter_rows())
        writer_registry.write_all(rows, self.config)
        return Dataset(name=self.config_name, config=self.config)

    def _resolve_order(self) -> tuple[str, ...]:
        order: list[str] = []
        resolved: set[str] = set()

        for column in self.config.columns:
            self._visit_order(column.name, (), resolved, order)

        return tuple(order)

    def _visit_order(
            self,
            name: str,
            pending: tuple[str, ...],
            resolved: set[str],
            order: list[str],
    ) -> None:
        if name in resolved:
            return
        if name in pending:
            cycle = " -> ".join([*pending, name])
            raise Exception(f"Circular column dependency detected: {cycle}")

        generator = self._generators.get(name)
        if generator is None:
            dependent = pending[-1] if pending else name
            raise Exception(f"Column {dependent!r} depends on unknown column {name!r}.")

        for dependency in generator.dependencies:
            self._visit_order(dependency, (*pending, name), resolved, order)

        resolved.add(name)
        order.append(name)
