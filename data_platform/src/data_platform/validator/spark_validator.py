from collections.abc import Iterable
from functools import reduce
from typing import Any

from pyspark.sql import DataFrame

from data_platform.model.assessment_model import AssessmentModel
from data_platform.model.violation_model import ViolationModel
from data_platform.util.validation_utils import require_columns
from data_platform.validator.validator_chain import ValidatorChain


class SparkValidatorChain(ValidatorChain):
    def combine(self, source: DataFrame, rejected: list[DataFrame]) -> DataFrame:
        return reduce(lambda left, right: left.unionByName(right, allowMissingColumns=True), rejected, source.limit(0))


class RequiredColumnsValidator:
    def __init__(self, columns: Iterable[str]) -> None:
        self.columns = tuple(columns)

    def validate(self, dataframe: DataFrame) -> AssessmentModel:
        require_columns(dataframe, self.columns)
        return AssessmentModel(dataframe, dataframe.limit(0))


class ColumnValidator:
    rule: str
    message: str

    def make_mask(self, dataframe: DataFrame) -> Any:
        raise NotImplementedError

    def validate(self, dataframe: DataFrame) -> AssessmentModel:
        rejected = dataframe.filter(~self.make_mask(dataframe))
        accepted = dataframe.filter(self.make_mask(dataframe))
        errors = (ViolationModel(self.rule, self.message),) if not rejected.isEmpty() else ()
        return AssessmentModel(accepted, rejected, errors)


class NotNullValidator(ColumnValidator):
    def __init__(self, column: str) -> None:
        self.column = column
        self.rule = f"{column}_not_null"
        self.message = f"{column} must not be null"

    def make_mask(self, dataframe: DataFrame) -> Any:
        return dataframe[self.column].isNotNull()


class NonNegativeValidator(ColumnValidator):
    def __init__(self, column: str) -> None:
        self.column = column
        self.rule = f"{column}_non_negative"
        self.message = f"{column} must be non-negative"

    def make_mask(self, dataframe: DataFrame) -> Any:
        return dataframe[self.column] >= 0


class PositiveValidator(ColumnValidator):
    def __init__(self, column: str) -> None:
        self.column = column
        self.rule = f"{column}_positive"
        self.message = f"{column} must be positive"

    def make_mask(self, dataframe: DataFrame) -> Any:
        return dataframe[self.column] > 0
