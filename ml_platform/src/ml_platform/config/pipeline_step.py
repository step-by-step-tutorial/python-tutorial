from enum import StrEnum


class PipelineStep(StrEnum):
    PREPROCESSOR = "preprocessor"
    ESTIMATOR = "estimator"
