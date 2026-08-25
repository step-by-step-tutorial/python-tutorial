from enum import StrEnum


class StorageEnvironment(StrEnum):
    RAW = "raw"
    CLEANED = "cleaned"
    ACCEPTED = "validated"
    REJECTED = "invalid"
    ENRICHED = "enriched"
