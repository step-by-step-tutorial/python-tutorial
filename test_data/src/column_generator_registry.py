from collections.abc import Sequence

from column_generator import (
    ColumnGenerator,
    DateWithRandomDayOffsetColumn,
    EmailFromSourceFieldsColumn,
    FixedColumn,
    FormulaColumn,
    LookupFromCsvColumn,
    ProductColumn,
    RandomDateColumn,
    RandomFromFileColumn,
    RandomFromMappedFileColumn,
    RandomIntColumn,
    SequenceColumn,
)
from schemas import ColumnModel
from validation_utils import require_not_blank


class ColumnGeneratorRegistry:
    generator_types: dict[str, type[ColumnGenerator]] = {
        "sequence": SequenceColumn,
        "fixed": FixedColumn,
        "random_int": RandomIntColumn,
        "random_date": RandomDateColumn,
        "random_from_file": RandomFromFileColumn,
        "random_from_mapped_file": RandomFromMappedFileColumn,
        "email_from_source_fields": EmailFromSourceFieldsColumn,
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

        return generator_type(column)

    @classmethod
    def get_all(cls, columns: Sequence[ColumnModel]) -> dict[str, ColumnGenerator]:
        return {column.name: cls.get_one(column) for column in columns}

    @classmethod
    def get_dependencies(cls, columns: Sequence[ColumnModel]) -> dict[str, tuple[str, ...]]:
        return {
            column.name: cls.get_one(column).dependencies
            for column in columns
        }
