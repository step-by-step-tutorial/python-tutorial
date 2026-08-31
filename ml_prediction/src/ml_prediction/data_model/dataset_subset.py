from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class DatasetSubset:
    features: pd.DataFrame
    target: pd.Series
