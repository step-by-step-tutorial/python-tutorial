from sklearn.base import ClassifierMixin
from sklearn.ensemble import RandomForestClassifier

from ml_prediction.config.settings import get_settings


class ClassifierBuilder:
    def __init__(self, dataset_name: str) -> None:
        self._dataset_name = dataset_name

    def build(self) -> ClassifierMixin:
        settings = get_settings(self._dataset_name)
        if settings.model_type != "random_forest":
            raise ValueError(f"Unsupported classifier type: {settings.model_type}")
        return RandomForestClassifier(
            n_estimators=settings.n_estimators,
            n_jobs=settings.n_jobs,
            max_depth=settings.max_depth,
            min_samples_split=settings.min_samples_split,
            min_samples_leaf=settings.min_samples_leaf,
            max_features=settings.max_features,
            bootstrap=settings.bootstrap,
            random_state=settings.random_state,
        )
