from typing import Any


class SparkAnalyzerChain:
    def __init__(self, analyzers: tuple[Any, ...] = ()) -> None:
        self.analyzers = analyzers

    def analyze(self, dataframe: Any) -> tuple[Any, ...]:
        return tuple(analyzer.analyze(dataframe) for analyzer in self.analyzers)
