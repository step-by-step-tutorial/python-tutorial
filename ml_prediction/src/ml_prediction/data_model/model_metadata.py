"""Compatibility imports for offline model metadata."""
from ml_prediction.offline_tracking.models import ModelMetadata

CURRENT_SCHEMA_VERSION = "1"
CURRENT_MODEL_VERSION = "1"

__all__ = ["CURRENT_MODEL_VERSION", "CURRENT_SCHEMA_VERSION", "ModelMetadata"]
