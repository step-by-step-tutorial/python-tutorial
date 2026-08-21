from collections.abc import Iterator

from collection_utils import order_dependencies
from column_generator_registry import ColumnGeneratorRegistry
from config_utils import read_config
from schemas import Dataset
from validation_utils import require_or_raise_map, \
    require_absent
from writer_registry import WriterRegistry


class DatasetGenerator:

    def __init__(self, config_name: str) -> None:
        self.config_name = config_name
        self.config = read_config(config_name)
        self.column_generators = ColumnGeneratorRegistry.get_all(self.config.columns)
        self.writers = WriterRegistry()
        self.ordered_column = order_dependencies(
            self.config.column_names,
            lambda name, pending, resolved, ordered: self.resolve_dependencies(name, pending, resolved, ordered)
        )

    def generate_rows(self) -> Iterator[dict[str, str]]:
        column_names = self.config.column_names
        row_count = self.config.row_count
        for row_index in range(row_count):
            values: dict[str, str] = {}
            for column_name in self.ordered_column:
                values[column_name] = self.column_generators[column_name].generate(values, row_index)
            yield {name: values[name] for name in column_names}

    def write(self) -> Dataset:
        self.writers.write_all(list[dict[str, str]](self.generate_rows()), self.config)
        return Dataset(name=self.config_name, config=self.config)

    def resolve_dependencies(self, name: str, pended: tuple[str, ...], resolved: list[str], ordered: list[str]) -> None:
        if name in resolved:
            return

        require_absent(pended, name)
        column_generator = require_or_raise_map(
            mapping=self.column_generators,
            key=name,
            error_message=f"Column {pended[-1] if pended else name} depends on unknown column {name}."
        )
        dependencies = column_generator.dependencies

        for dependency in dependencies:
            self.resolve_dependencies(dependency, (*pended, name), resolved, ordered)

        resolved.append(name)
        ordered.append(name)
