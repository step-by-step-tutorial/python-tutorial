from dataclasses import dataclass, field, fields
from enum import StrEnum
from typing import Any


class ColumnType(StrEnum):
    STRING = "string"
    INTEGER = "integer"
    DOUBLE = "double"
    BOOLEAN = "boolean"
    DATE = "date"
    TIMESTAMP = "timestamp"


def column(name: str, column_type: ColumnType) -> Any:
    return field(default=name, metadata={"column_type": column_type})


@dataclass(frozen=True)
class AttributeModel:
    @property
    def columns(self) -> tuple[str, ...]:
        return tuple(getattr(self, attribute.name) for attribute in fields(self))

    def columns_of(self, *column_types: ColumnType) -> tuple[str, ...]:
        return tuple(
            getattr(self, attribute.name)
            for attribute in fields(self)
            if attribute.metadata["column_type"] in column_types
        )

    def spark_schema(self) -> Any:
        from pyspark.sql.types import (
            BooleanType, DateType, DoubleType, IntegerType, StringType, StructField, StructType, TimestampType,
        )

        spark_types = {
            ColumnType.STRING: StringType(),
            ColumnType.INTEGER: IntegerType(),
            ColumnType.DOUBLE: DoubleType(),
            ColumnType.BOOLEAN: BooleanType(),
            ColumnType.DATE: DateType(),
            ColumnType.TIMESTAMP: TimestampType(),
        }
        return StructType([
            StructField(getattr(self, attribute.name), spark_types[attribute.metadata["column_type"]], nullable=True)
            for attribute in fields(self)
        ])
