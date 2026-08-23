from enum import StrEnum


class DataLakeEnvironment(StrEnum):
    RAW = "raw"
    CLEANED = "cleaned"
    ENRICHED = "enriched"
