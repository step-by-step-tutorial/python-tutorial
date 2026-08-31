from dataclasses import dataclass

from ml_prediction.data_model.dataset_partition import DatasetPartition


@dataclass(frozen=True)
class DatasetPartitions:
    train: DatasetPartition
    validation: DatasetPartition
    test: DatasetPartition
