from ml_prediction.dataset.tabular_dataset import PreparedTrainingData, TabularDataset


class HouseDataset(TabularDataset):
    target_is_numeric = True
