from typing import Any

import pandas as pd

from data_platform.pipeline.pipeline import Pipeline


class InmemoryPipeline(Pipeline):

    def combine(self, dataframes: list[pd.DataFrame]) -> pd.DataFrame:
        return pd.concat(dataframes, ignore_index=True)

    def count(self, dataframe: Any) -> int:
        return len(dataframe)

    def is_empty(self, dataframe: Any) -> bool:
        return len(dataframe) == 0

    def to_dataframe(self, data: Any) -> pd.DataFrame:
        return pd.DataFrame(data)
