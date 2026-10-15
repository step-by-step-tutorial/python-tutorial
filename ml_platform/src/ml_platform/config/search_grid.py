from ml_platform.config.model_type import ModelType

_TREE_ENSEMBLE_GRID = {
    "n_estimators": [100, 300, 500],
    "max_depth": [None, 10, 20],
    "min_samples_split": [2, 4],
    "min_samples_leaf": [1, 2],
    "max_features": [0.7, 1.0],
}

SEARCH_GRIDS: dict[ModelType, dict[str, list]] = {
    ModelType.RANDOM_FOREST: _TREE_ENSEMBLE_GRID,
    ModelType.EXTRA_TREES: _TREE_ENSEMBLE_GRID,
    ModelType.GRADIENT_BOOSTING: _TREE_ENSEMBLE_GRID,
    ModelType.HIST_GRADIENT_BOOSTING: {
        "max_iter": [100, 300, 500],
        "max_depth": [None, 10, 20],
        "min_samples_leaf": [10, 20],
        "max_features": [0.7, 1.0],
    },
}
