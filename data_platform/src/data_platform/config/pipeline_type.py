from enum import StrEnum


class PipelineType(StrEnum):
    INMEMORY = "inmemory"
    SPARK = "spark"
