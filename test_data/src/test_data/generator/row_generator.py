from collections.abc import Iterator, Sequence

from test_data.generator.column_generator_registry import ColumnGeneratorRegistry
from test_data.model.schemas import ColumnModel, ConfigModel
from test_data.util.collection_utils import topological_sort


class RowGenerator:
    def __init__(self, config: ConfigModel, columns: Sequence[ColumnModel]) -> None:
        self.config = config
        self.column_generators = ColumnGeneratorRegistry.get_all(columns)
        self.ordered_columns = topological_sort(ColumnGeneratorRegistry.get_dependencies(columns))

    def generate_rows(self) -> Iterator[dict[str, str]]:
        for row_index in range(self.config.row_count):
            values: dict[str, str] = {}
            for column_name in self.ordered_columns:
                values[column_name] = self.column_generators[column_name].generate(values, row_index)
            yield {name: values[name] for name in self.config.column_names}
