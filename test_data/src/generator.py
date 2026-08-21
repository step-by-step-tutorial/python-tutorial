from collections.abc import Iterator

from column_generator_registry import ColumnGeneratorRegistry
from config_utils import read_config
from datasets import Dataset
from validation_utils import require_not_blank, require_or_raise_tuple, require_or_raise_map, \
    require_absent
from writer_registry import WriterRegistry


class DataGenerator:

    def __init__(self, config_name: str) -> None:
        self.config_name = config_name
        self.config = read_config(config_name)
        self.column_generators = ColumnGeneratorRegistry.get_all(self.config.columns)
        self.writers = WriterRegistry()
        self._order = self._resolve_order()

    def generate_rows(self) -> Iterator[dict[str, str]]:
        headers = self.config.headers
        for row_index in range(self.config.row_count):
            values: dict[str, str] = {}
            for name in self._order:
                values[name] = self.column_generators[name].generate(values, row_index)
            yield {name: values[name] for name in headers}

    def write(self) -> Dataset:
        self.writers.write_all(list[dict[str, str]](self.generate_rows()), self.config)
        return Dataset(name=self.config_name, config=self.config)

    def _resolve_order(self) -> tuple[str, ...]:
        order: list[str] = []
        resolved: set[str] = set()

        for column in self.config.columns:
            pending = ()
            self._visit_order(column.name, pending, resolved, order)

        return tuple(order)

    def _visit_order(self, name: str, pending: tuple[str, ...], resolved: set[str], order: list[str]) -> None:
        if name in resolved:
            return

        require_absent(pending, name)
        dependencies = require_or_raise_map(
            mapping=self.column_generators,
            key=name,
            error_message=f"Column {pending[-1] if pending else name} depends on unknown column {name}."
        ).dependencies

        for dependency in dependencies:
            self._visit_order(dependency, (*pending, name), resolved, order)

        resolved.add(name)
        order.append(name)
