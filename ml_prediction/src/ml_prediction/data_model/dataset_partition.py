from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class DatasetPartition:
    features: pd.DataFrame
    target: pd.Series
