from typing import Any, Protocol


class Enricher(Protocol):
    def enrich(self, dataframe: Any) -> Any:
        ...
