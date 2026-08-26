from collections.abc import Iterable

from pyspark.sql import DataFrame

from data_platform.util.dataframe_utils import empty_compatible_dataframe
from data_platform.util.collection_utils import find_missing_columns
from data_platform.validators.assessment import Assessment
from data_platform.validators.violation import Violation


class RequiredColumnsValidator:
    def __init__(self, columns: Iterable[str]) -> None:
        self.columns = tuple(columns)

    def validate(self, dataframe: DataFrame) -> Assessment:
        missing = find_missing_columns(dataframe, self.columns)
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")
        return Assessment(dataframe, empty_compatible_dataframe(dataframe))


class _ColumnValidator:
    rule: str
    message: str

    def validate(self, dataframe: DataFrame) -> Assessment:
        rejected = dataframe.filter(~self.make_mask(dataframe))
        accepted = dataframe.filter(self.make_mask(dataframe))
        errors = (Violation(self.rule, self.message),) if not rejected.isEmpty() else ()
        return Assessment(accepted, rejected, errors)


class NotNullValidator(_ColumnValidator):
    def __init__(self, column: str) -> None:
        self.column = column
        self.rule = f"{column}_not_null"
        self.message = f"{column} must not be null"

    def make_mask(self, dataframe: DataFrame):
        return dataframe[self.column].isNotNull()


class NonNegativeValidator(_ColumnValidator):
    def __init__(self, column: str) -> None:
        self.column = column
        self.rule = f"{column}_non_negative"
        self.message = f"{column} must be non-negative"

    def make_mask(self, dataframe: DataFrame):
        return dataframe[self.column] >= 0


class PositiveValidator(_ColumnValidator):
    def __init__(self, column: str) -> None:
        self.column = column
        self.rule = f"{column}_positive"
        self.message = f"{column} must be positive"

    def make_mask(self, dataframe: DataFrame):
        return dataframe[self.column] > 0
