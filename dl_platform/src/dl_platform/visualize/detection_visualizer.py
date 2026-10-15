from collections.abc import Sequence

import torch
from torch import Tensor
from torchvision.utils import draw_bounding_boxes

from dl_platform.model.detection_model import DetectionModel

PALETTE = ("#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4", "#42d4f4", "#f032e6", "#bfef45", "#469990", "#9a6324")


class DetectionVisualizer:
    """Draws one colored box per detection, with its label and score; each label of a task keeps its color."""

    def __init__(self, labels: Sequence[str]) -> None:
        self._colors = {label: PALETTE[index % len(PALETTE)] for index, label in enumerate(labels)}

    def render(self, image: Tensor, detections: Sequence[DetectionModel]) -> Tensor:
        if not detections:
            return image
        return draw_bounding_boxes(
            image,
            boxes=torch.tensor([detection.box for detection in detections]),
            labels=[f"{detection.label} {detection.score:.2f}" for detection in detections],
            colors=[self._colors[detection.label] for detection in detections],
            width=3,
        )
