from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class FeaturesAndTarget:
    features: pd.DataFrame
    target: pd.Series
