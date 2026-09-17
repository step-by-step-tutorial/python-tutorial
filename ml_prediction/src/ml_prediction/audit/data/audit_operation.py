from enum import StrEnum


class AuditOperation(StrEnum):
    TRAINING = "training"
    PREDICTION = "prediction"
