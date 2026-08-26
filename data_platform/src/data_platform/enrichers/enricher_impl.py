from collections.abc import Callable
import hashlib
from typing import Any

from data_platform.enrichers.enricher_chain import EnricherChain


class CalculateColumnEnricher:
    def __init__(self, column: str, function: Callable[[Any], Any]) -> None:
        self.column, self.function = column, function

    def enrich(self, dataframe: Any) -> Any:
        dataframe[self.column] = dataframe.apply(self.function, axis=1)
        return dataframe


class MultiplyColumnsEnricher:
    def __init__(self, left: str, right: str, target: str, decimals: int = 2) -> None:
        self.left, self.right, self.target, self.decimals = left, right, target, decimals

    def enrich(self, dataframe: Any) -> Any:
        dataframe[self.target] = (dataframe[self.left] * dataframe[self.right]).round(self.decimals)
        return dataframe


class PercentageEnricher:
    def __init__(self, value: str, percent: str, target: str, decimals: int = 2) -> None:
        self.value, self.percent, self.target, self.decimals = value, percent, target, decimals

    def enrich(self, dataframe: Any) -> Any:
        dataframe[self.target] = (dataframe[self.value] * dataframe[self.percent] / 100).round(self.decimals)
        return dataframe


class CopyColumnEnricher:
    def __init__(self, source: str, target: str, decimals: int | None = None) -> None:
        self.source, self.target, self.decimals = source, target, decimals

    def enrich(self, dataframe: Any) -> Any:
        values = dataframe[self.source]
        dataframe[self.target] = values.round(self.decimals) if self.decimals is not None else values
        return dataframe


class DivideColumnsEnricher:
    def __init__(self, numerator: str, denominator: str, target: str, decimals: int = 2) -> None:
        self.numerator, self.denominator, self.target, self.decimals = numerator, denominator, target, decimals

    def enrich(self, dataframe: Any) -> Any:
        dataframe[self.target] = (dataframe[self.numerator] / dataframe[self.denominator]).round(self.decimals)
        return dataframe


class DatetimePartEnricher:
    def __init__(self, source: str, part: str, target: str) -> None:
        self.source, self.part, self.target = source, part, target

    def enrich(self, dataframe: Any) -> Any:
        dataframe[self.target] = getattr(dataframe[self.source].dt, self.part)
        return dataframe


class HashColumnsEnricher:
    def __init__(self, columns: tuple[str, ...], target: str, separator: str = "|") -> None:
        self.columns, self.target, self.separator = columns, target, separator

    def enrich(self, dataframe: Any) -> Any:
        def digest(row: Any) -> str:
            values = ["" if row[column] is None else str(row[column]) for column in self.columns]
            return hashlib.sha256(self.separator.join(values).encode("utf-8")).hexdigest()
        dataframe[self.target] = dataframe.apply(digest, axis=1)
        return dataframe
