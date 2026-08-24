from typing import Protocol


class DataExposer(Protocol):
    def expose(self, enriched_data_path: str) -> None: ...

