from dataclasses import dataclass

from ml_prediction.data_model.features_and_target import FeaturesAndTarget


@dataclass(frozen=True)
class DatasetSplit:
    train: FeaturesAndTarget
    validation: FeaturesAndTarget
    test: FeaturesAndTarget
