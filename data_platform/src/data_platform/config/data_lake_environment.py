from enum import StrEnum


class StorageEnvironment(StrEnum):
    RAW = "raw"
    CLEANED = "cleaned"
    ENRICHED = "enriched"

