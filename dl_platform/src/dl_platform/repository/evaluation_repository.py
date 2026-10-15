import logging
from collections.abc import Sequence
from pathlib import Path

from dl_platform.model.evaluation_model import EvaluationModel
from dl_platform.util.csv_utils import write_rows

logger = logging.getLogger(__name__)

COLUMNS = ("label", "images", "objects", "ap", "ap50", "ar")


class EvaluationRepository:

    def save(self, path: Path, results: Sequence[EvaluationModel]) -> Path:
        write_rows(path, [result.to_dict() for result in results], COLUMNS)
        logger.info("Saved evaluation: path=%s rows=%s", path, len(results))
        return path
