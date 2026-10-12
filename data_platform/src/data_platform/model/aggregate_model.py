from dataclasses import dataclass


@dataclass(frozen=True)
class AggregateModel:
    group_column: str
    value_column: str
    aggregation_function: str
    output_column: str = ""
