from dataclasses import dataclass

from ml_prediction.data_model.dataset_subset import DatasetSubset


@dataclass(frozen=True)
class DatasetSplit:
    train: DatasetSubset
    validation: DatasetSubset
    test: DatasetSubset
