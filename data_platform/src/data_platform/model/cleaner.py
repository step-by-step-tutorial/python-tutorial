from typing import Any, Protocol


class Cleaner(Protocol):
    def clean(self, dataframe: Any) -> Any:
        ...
