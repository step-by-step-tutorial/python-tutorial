from dataclasses import dataclass


@dataclass(frozen=True)
class StorageObject:
    storage: str
    path: str

