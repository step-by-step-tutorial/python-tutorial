from typing import Any


class SparkCleanerChain:
    def __init__(self, cleaners: tuple[Any, ...] = ()) -> None:
        self.cleaners = cleaners

    def clean(self, dataframe: Any) -> Any:
        for cleaner in self.cleaners:
            dataframe = cleaner.clean(dataframe)
        return dataframe
