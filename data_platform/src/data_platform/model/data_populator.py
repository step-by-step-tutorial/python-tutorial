from typing import Protocol


class DataPopulator(Protocol):
    def populate(self, enriched_data_path: str) -> None: ...
