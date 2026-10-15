from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from dl_platform.model.detection_model import DetectionModel


@dataclass(frozen=True)
class ImageDetectionsModel:
    image_path: Path
    detections: tuple[DetectionModel, ...]

    def to_rows(self) -> list[dict[str, str | float]]:
        return [{"image": self.image_path.name} | detection.to_dict() for detection in self.detections]

    @staticmethod
    def count_by_label(results: Iterable["ImageDetectionsModel"]) -> Counter[str]:
        return Counter(detection.label for result in results for detection in result.detections)
