from collections.abc import Mapping

from test_data.generator.column.column_generator import ColumnGenerator, Row
from test_data.model.column_model import ColumnModel
from test_data.model.settings_model import SettingsModel
from test_data.repository.source_repository import SourceRepository
from test_data.util.csv_utils import filter_rows, rows_with_values
from test_data.util.file_utils import list_directory_names
from test_data.util.validation_utils import default_if_blank, require_exactly_one, require_key, require_not_blank


class RandomFromFileColumn(ColumnGenerator):

    def validate(self) -> None:
        self.require("file")

    def generate(self, row: Row, row_index: int) -> str:
        return self.rand.choice(self.source_repository.read_text_file(self.model.file))  # type: ignore[arg-type]


class RandomFromDirectoryColumn(ColumnGenerator):
    def validate(self) -> None:
        self.require("file")

    def generate(self, row: Row, row_index: int) -> str:
        directories = list_directory_names(self.source_repository.project_path(require_not_blank(self.model.file)))
        excluded = set(self.model.exclude_directories or ())
        directories = [directory for directory in directories if directory not in excluded]
        if not directories:
            raise ValueError(f"No directories found for column {self.model.name}.")
        return self.rand.choice(directories)


class RandomFromMappedFileColumn(ColumnGenerator):

    def __init__(self, model: ColumnModel, settings: SettingsModel, source_repository: SourceRepository) -> None:
        self.file_columns = None
        self.separator = None
        super().__init__(model, settings, source_repository)

    def validate(self) -> None:
        self.require("source_field", "mapping_file", "key_column")
        require_exactly_one(
            first=self.model.file_column,
            second=self.model.file_columns,
            error_message=f"Column {self.model.name} of type {self.model.type} requires: XOR of file_column and file_columns."
        )

        self.file_columns = default_if_blank(value=self.model.file_columns, default=(self.model.file_column,))
        self.separator = default_if_blank(value=self.model.separator, default=" ")

    @property
    def dependencies(self) -> tuple[str, ...]:
        return (require_not_blank(self.model.source_field),)

    def generate(self, row: Row, row_index: int) -> str:
        key = self.get_by_source(row)
        parts: list[str] = []
        for value_column in self.file_columns:
            mapping = self.source_repository.read_csv_file(
                require_not_blank(self.model.mapping_file),
                require_not_blank(self.model.key_column),
                value_column
            )
            source_file = self.get_by_key(mapping, key)
            parts.append(self.rand.choice(self.source_repository.read_text_file(source_file)))

        return self.separator.join(parts)


class RandomFromMappedCsvColumn(ColumnGenerator):
    """A value from a CSV row whose key_column matches the source field, optionally filtered.

    Columns with the same mapping settings share the selected row of each generated row, so values taken
    from one CSV record (street, city, postcode) stay consistent.
    """

    def __init__(self, model: ColumnModel, settings: SettingsModel, source_repository: SourceRepository) -> None:
        self._candidates: dict[tuple[object, ...], tuple[Mapping[str, str], ...]] = {}
        super().__init__(model, settings, source_repository)

    def validate(self) -> None:
        self.require("source_field", "key_column")
        require_exactly_one(
            first=self.model.value_column,
            second=self.model.value_template,
            error_message=f"Column {self.model.name} requires exactly one of value_column or value_template."
        )
        require_exactly_one(
            first=self.model.mapping_file,
            second=self.model.file_template,
            error_message=f"Column {self.model.name} requires exactly one of mapping_file or file_template."
        )

    @property
    def dependencies(self) -> tuple[str, ...]:
        return (require_not_blank(self.model.source_field),)

    def generate(self, row: Row, row_index: int) -> str:
        source_value = self.get_by_source(row)
        mapping_file = self._mapping_file(source_value)
        candidates_key = self._candidates_key(mapping_file, source_value)
        selected = self.source_repository.select_row(
            candidates_key + (row_index,),
            lambda: self.rand.choice(self._candidate_rows(candidates_key, mapping_file, source_value)),
        )
        return self._value(selected)

    def _mapping_file(self, source_value: str) -> str:
        if self.model.file_template is None:
            return require_not_blank(self.model.mapping_file)

        source_field = require_not_blank(self.model.source_field)
        return self.model.file_template.format(**{source_field: source_value})

    def _candidates_key(self, mapping_file: str, source_value: str) -> tuple[object, ...]:
        return (
            mapping_file,
            source_value,
            self.model.key_column,
            self.model.filter_column,
            tuple(self.model.filter_values or ()),
            tuple(self.model.filter_fallback_values or ()),
            tuple(self.model.required_columns or ()),
            self.model.candidate_limit,
        )

    def _candidate_rows(
            self, key: tuple[object, ...], mapping_file: str, source_value: str
    ) -> tuple[Mapping[str, str], ...]:
        """Rows matching the source value, then the filter (or its fallback), then the required columns."""
        if key not in self._candidates:
            rows = self.source_repository.read_csv_rows(
                mapping_file, require_not_blank(self.model.key_column), source_value, self.model.candidate_limit
            )
            if self.model.filter_column and self.model.filter_values:
                filtered = filter_rows(rows, self.model.filter_column, self.model.filter_values)
                if not filtered and self.model.filter_fallback_values:
                    filtered = filter_rows(rows, self.model.filter_column, self.model.filter_fallback_values)
                rows = filtered
            if self.model.required_columns:
                rows = rows_with_values(rows, self.model.required_columns)
            self._candidates[key] = rows

        if not self._candidates[key]:
            raise ValueError(f"No rows found for '{source_value}' in mapping for column {self.model.name}.")
        return self._candidates[key]

    def _value(self, selected: Mapping[str, str]) -> str:
        if self.model.value_template is not None:
            try:
                return self.model.value_template.format_map(selected)
            except (KeyError, ValueError) as error:
                raise ValueError(f"Column {self.model.name} has an invalid value template.") from error

        return require_key(
            selected,
            require_not_blank(self.model.value_column),
            f"Column {self.model.name} has no value in the selected address record.",
        )


class LookupFromCsvColumn(ColumnGenerator):

    def validate(self) -> None:
        self.require("source_field", "mapping_file", "key_column", "value_column")

    @property
    def dependencies(self) -> tuple[str, ...]:
        return (require_not_blank(self.model.source_field),)

    def generate(self, row: Row, row_index: int) -> str:
        mapping = self.source_repository.read_csv_file(
            require_not_blank(self.model.mapping_file),
            require_not_blank(self.model.key_column),
            require_not_blank(self.model.value_column),
        )
        return self.get_by_key(mapping, self.get_by_source(row))
