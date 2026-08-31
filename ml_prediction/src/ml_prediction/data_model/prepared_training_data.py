from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class PreparedTrainingData:
    features: pd.DataFrame
    target: pd.Series
