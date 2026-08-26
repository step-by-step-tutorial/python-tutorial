from typing import Any


class SparkEnricherChain:
    def __init__(self, enrichers: tuple[Any, ...] = ()) -> None:
        self.enrichers = enrichers

    def enrich(self, dataframe: Any) -> Any:
        for enricher in self.enrichers:
            dataframe = enricher.enrich(dataframe)
        return dataframe
