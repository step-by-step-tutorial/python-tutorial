from collections.abc import Sequence

from test_data.generator.column_generator import (
    ColumnGenerator,
    ConcatFromSourceFieldsColumn,
    DateWithRandomDayOffsetColumn,
    EmailFromSourceFieldsColumn,
    FixedColumn,
    FormulaColumn,
    LookupFromCsvColumn,
    ProductColumn,
    RandomDateColumn,
    RandomFloatColumn,
    RandomBooleanColumn,
    RandomTimestampColumn,
    RandomFromFileColumn,
    RandomFromMappedCsvColumn,
    RandomFromDirectoryColumn,
    RandomFromMappedFileColumn,
    RandomIntColumn,
    SequenceColumn,
)
from test_data.model.schemas import ColumnModel
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

    @classmethod
    def get_one(cls, column: ColumnModel) -> ColumnGenerator:
        generator_name = column.method or column.type
        generator_type = cls.generator_types.get(generator_name)
        require_not_blank(generator_type, f"Unsupported column generator: {generator_name}")

        generator = generator_type(column)
        if not column.nullable:
            return generator
        return NullableColumnGenerator(generator, column.null_probability)

    @classmethod
    def get_all(cls, columns: Sequence[ColumnModel]) -> dict[str, ColumnGenerator]:
        return {column.name: cls.get_one(column) for column in columns}

    @classmethod
    def get_dependencies(cls, columns: Sequence[ColumnModel]) -> dict[str, tuple[str, ...]]:
        return {
            column.name: cls.get_one(column).dependencies
            for column in columns
        }


class NullableColumnGenerator(ColumnGenerator):
    def __init__(self, delegate: ColumnGenerator, probability: float | None):
        self.delegate = delegate
        self.probability = 0.2 if probability is None else probability
        super().__init__(delegate.model)

    @property
    def dependencies(self) -> tuple[str, ...]:
        return self.delegate.dependencies

    def generate(self, row: dict[str, str], row_index: int) -> str:
        if self.rand.random() < self.probability:
            return ""
        return self.delegate.generate(row, row_index)
