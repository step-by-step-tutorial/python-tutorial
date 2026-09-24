from enum import StrEnum


class PipelineStep(StrEnum):
    PREPROCESSOR = "preprocessor"
    REGRESSOR = "regressor"
    CLASSIFIER = "classifier"
