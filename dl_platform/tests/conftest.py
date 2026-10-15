from pathlib import Path

import pytest
import torch
from torch import Tensor, nn

from dl_platform.config.detection_tasks import VEHICLE_DETECTION
from dl_platform.detector.object_detector import ObjectDetector
from dl_platform.model.detection_task_model import DetectionTaskModel
from dl_platform.model.settings_model import SettingsModel
from dl_platform.repository.image_repository import ImageRepository

CATEGORIES = ("__background__", "person", "bicycle", "car", "dog")


class FakeDetectionModel(nn.Module):
    """Returns the same detections for every image, in the torchvision detection output format."""

    def __init__(self, boxes: list[list[float]], labels: list[int], scores: list[float]) -> None:
        super().__init__()
        self._output = {
            "boxes": torch.tensor(boxes, dtype=torch.float32).reshape(-1, 4),
            "labels": torch.tensor(labels, dtype=torch.int64),
            "scores": torch.tensor(scores, dtype=torch.float32),
        }

    def forward(self, images: list[Tensor]) -> list[dict[str, Tensor]]:
        return [self._output for _ in images]


def make_detector(boxes, labels, scores) -> ObjectDetector:
    return ObjectDetector(FakeDetectionModel(boxes, labels, scores), CATEGORIES, lambda image: image.float() / 255)


def make_settings(tmp_path: Path, task: DetectionTaskModel = VEHICLE_DETECTION, **overrides) -> SettingsModel:
    values = {
        "task": task,
        "data_dir": tmp_path / "data",
        "model_dir": tmp_path / "models",
        "output_dir": tmp_path / "output",
        "audit_dir": tmp_path / "audit",
    }
    return SettingsModel(**(values | overrides))


def make_image(height: int = 48, width: int = 64, seed: int = 0) -> Tensor:
    generator = torch.Generator().manual_seed(seed)
    return torch.randint(0, 256, (3, height, width), dtype=torch.uint8, generator=generator)


def write_images(directory: Path, *names: str) -> list[Path]:
    repository = ImageRepository()
    return [repository.save(directory / name, make_image(seed=seed)) for seed, name in enumerate(names)]


@pytest.fixture
def vehicle_settings(tmp_path: Path) -> SettingsModel:
    settings = make_settings(tmp_path)
    write_images(settings.input_dir, "street.jpg", "parking.png")
    return settings
