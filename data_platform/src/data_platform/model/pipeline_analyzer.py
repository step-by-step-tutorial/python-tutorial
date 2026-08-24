from typing import Protocol


class PipelineAnalyzer(Protocol):
    def analyze(self, enriched_data_path: str) -> None: ...

