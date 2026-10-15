from collections.abc import Iterator

from test_data_platform.generator.column.column_generator_registry import ColumnGeneratorRegistry
from test_data_platform.model.config_model import ConfigModel
from test_data_platform.model.settings_model import SettingsModel
from test_data_platform.repository.source_repository import SourceRepository
from test_data_platform.util.collection_utils import topological_sort


class RowGenerator:
    def __init__(self, config: ConfigModel, settings: SettingsModel) -> None:
        self.config = config
        # One source repository per dataset run: source files are read once and mapped rows are shared by its columns.
        registry = ColumnGeneratorRegistry(settings, SourceRepository(settings))
        self.column_generators = registry.get_all(config.columns)
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
