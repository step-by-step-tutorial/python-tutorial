from enum import StrEnum


class ModelType(StrEnum):
    RANDOM_FOREST = "random_forest"
    EXTRA_TREES = "extra_trees"
    GRADIENT_BOOSTING = "gradient_boosting"
    HIST_GRADIENT_BOOSTING = "hist_gradient_boosting"
