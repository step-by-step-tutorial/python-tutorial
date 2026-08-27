import logging

import pandas as pd

from ml_prediction.dataset.dataset import Dataset

logger = logging.getLogger(__name__)


class HouseDataset(Dataset):
    def load(self) -> pd.DataFrame:
        logger.info(f"Loading house dataset: path={self.path}")
        dataframe = pd.read_csv(self.path)
        logger.info(f"House dataset loaded: rows={len(dataframe)} columns={len(dataframe.columns)}")
        return dataframe

    def training_frame(self, target_column: str) -> pd.DataFrame:
        dataframe = self.load().copy()
        dataframe[target_column] = pd.to_numeric(dataframe[target_column], errors="coerce")
        dataframe = dataframe.dropna(subset=[target_column])
        logger.info("Prepared training frame: rows=%s target=%s", len(dataframe), target_column)
        return dataframe
