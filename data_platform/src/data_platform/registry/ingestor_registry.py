from typing import Any

from data_platform.registry.base_registry import Registry


class IngestorRegistry(Registry[Any]):
    def __init__(self) -> None:
        super().__init__("ingestor")


ingestor_registry = IngestorRegistry()
