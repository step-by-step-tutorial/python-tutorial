from collections.abc import Iterator

from collection_utils import order_dependencies
from column_generator import ColumnGenerator
from schemas import ConfigModel
from validation_utils import require_absent, require_or_raise_map


class RowGenerator:
    def __init__(self, config: ConfigModel, column_generators: dict[str, ColumnGenerator]) -> None:
        self.config = config
        self.column_generators = column_generators
        self.ordered_columns = order_dependencies(config.column_names, self.resolve_dependencies)

    def generate_rows(self) -> Iterator[dict[str, str]]:
        for row_index in range(self.config.row_count):
            values: dict[str, str] = {}
            for column_name in self.ordered_columns:
                values[column_name] = self.column_generators[column_name].generate(values, row_index)
            yield {name: values[name] for name in self.config.column_names}

    def resolve_dependencies(
            self,
            name: str,
            pending: tuple[str, ...],
            resolved: list[str],
            ordered: list[str],
    ) -> None:
        if name in resolved:
            return

        require_absent(pending, name)
        column_generator = require_or_raise_map(
            mapping=self.column_generators,
            key=name,
            error_message=f"Column {pending[-1] if pending else name} depends on unknown column {name}.",
        )

        for dependency in column_generator.dependencies:
            self.resolve_dependencies(dependency, (*pending, name), resolved, ordered)

        resolved.append(name)
        ordered.append(name)
