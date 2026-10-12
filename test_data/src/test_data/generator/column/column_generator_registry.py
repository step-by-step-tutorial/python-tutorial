from collections.abc import Sequence

from test_data.generator.column.column_generator import (
    ColumnGenerator,
    ConditionalColumnGenerator,
    NullableColumnGenerator,
)
from test_data.generator.column.derived_columns import (
    ConcatFromSourceFieldsColumn,
    DateWithRandomDayOffsetColumn,
    EmailFromSourceFieldsColumn,
    FormulaColumn,
    ProductColumn,
)
from test_data.generator.column.random_columns import (
    RandomBooleanColumn,
    RandomDateColumn,
    RandomFloatColumn,
    RandomIntColumn,
    RandomTimestampColumn,
)
from test_data.generator.column.simple_columns import FixedColumn, SequenceColumn
from test_data.generator.column.source_file_columns import (
    LookupFromCsvColumn,
    RandomFromDirectoryColumn,
    RandomFromFileColumn,
    RandomFromMappedCsvColumn,
    RandomFromMappedFileColumn,
)
from test_data.model.column_model import ColumnModel
from test_data.model.settings_model import SettingsModel
from test_data.repository.source_repository import SourceRepository
from test_data.util.validation_utils import require_not_blank


class ColumnGeneratorRegistry:
    generator_types: dict[str, type[ColumnGenerator]] = {
        "sequence": SequenceColumn,
        "fixed": FixedColumn,
        "random_int": RandomIntColumn,
        "random_float": RandomFloatColumn,
        "random_bool": RandomBooleanColumn,
        "random_date": RandomDateColumn,
        "random_timestamp": RandomTimestampColumn,
        "random_from_file": RandomFromFileColumn,
        "random_from_directory": RandomFromDirectoryColumn,
        "random_from_mapped_csv": RandomFromMappedCsvColumn,
        "random_from_mapped_file": RandomFromMappedFileColumn,
        "email_from_source_fields": EmailFromSourceFieldsColumn,
        "concat_from_source_fields": ConcatFromSourceFieldsColumn,
        "lookup_from_csv": LookupFromCsvColumn,
        "product_of_source_fields": ProductColumn,
        "formula": FormulaColumn,
        "date_with_random_day_offset": DateWithRandomDayOffsetColumn,
    }

    def __init__(self, settings: SettingsModel, source_repository: SourceRepository) -> None:
        self._settings = settings
        self._source_repository = source_repository

    def get_one(self, column: ColumnModel) -> ColumnGenerator:
        generator_name = column.method or column.type
        generator_type = self.generator_types.get(generator_name)
        require_not_blank(generator_type, f"Unsupported column generator: {generator_name}")

        generator = generator_type(column, self._settings, self._source_repository)
        if column.nullable:
            generator = NullableColumnGenerator(generator, column.null_probability)
        if column.present_when:
            generator = ConditionalColumnGenerator(generator, column.present_when)
        return generator

    def get_all(self, columns: Sequence[ColumnModel]) -> dict[str, ColumnGenerator]:
        return {column.name: self.get_one(column) for column in columns}
