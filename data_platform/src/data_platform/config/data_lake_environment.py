from enum import StrEnum


class StorageEnvironment(StrEnum):
    RAW = "raw"
    CLEANED = "cleaned"
    VALIDATED = "validated"
    INVALID = "invalid"
    ENRICHED = "enriched"
