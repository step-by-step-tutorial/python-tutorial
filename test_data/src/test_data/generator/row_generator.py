from collections.abc import Iterator

from test_data.generator.column_generator_registry import ColumnGeneratorRegistry
from test_data.model.schemas import ConfigModel
from test_data.util.collection_utils import topological_sort


class RowGenerator:
    def __init__(self, config: ConfigModel) -> None:
        self.config = config
        self.column_generators = ColumnGeneratorRegistry.get_all(config.columns)
        # Columns are generated after the columns they are derived from.
        self.ordered_columns = topological_sort(
            {name: generator.dependencies for name, generator in self.column_generators.items()}
        )

    def generate_rows(self) -> Iterator[dict[str, str]]:
        for row_index in range(self.config.row_count):
            values: dict[str, str] = {}
            for column_name in self.ordered_columns:
                values[column_name] = self.column_generators[column_name].generate(values, row_index)
            yield {name: values[name] for name in self.config.column_names}
