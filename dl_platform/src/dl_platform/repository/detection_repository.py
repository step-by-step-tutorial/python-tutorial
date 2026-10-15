import logging
from collections.abc import Sequence
from pathlib import Path

from dl_platform.model.image_detections_model import ImageDetectionsModel
from dl_platform.util.csv_utils import write_rows

logger = logging.getLogger(__name__)

COLUMNS = ("image", "label", "score", "x_min", "y_min", "x_max", "y_max")


class DetectionRepository:

    def save(self, path: Path, results: Sequence[ImageDetectionsModel]) -> Path:
        rows = [row for result in results for row in result.to_rows()]
        write_rows(path, rows, COLUMNS)
        logger.info("Saved detections: path=%s rows=%s", path, len(rows))
        return path
