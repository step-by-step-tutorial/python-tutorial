from collections.abc import Callable, Sequence

import torch
from torch import Tensor, nn

from dl_platform.model.detection_model import DetectionModel


class ObjectDetector:
    """Runs a detection model on one image and keeps the detections of the requested labels."""

    def __init__(
            self,
            model: nn.Module,
            categories: Sequence[str],
            transform: Callable[[Tensor], Tensor],
            device: str = "cpu",
    ) -> None:
        self._model = model.to(device).eval()
        self._categories = categories
        self._transform = transform
        self._device = device

    @property
    def categories(self) -> Sequence[str]:
        return self._categories

    @torch.inference_mode()
    def detect(self, image: Tensor, labels: Sequence[str], score_threshold: float) -> tuple[DetectionModel, ...]:
        output = self._model([self._transform(image).to(self._device)])[0]
        detections = zip(output["boxes"].tolist(), output["labels"].tolist(), output["scores"].tolist(), strict=True)
        return tuple(
            DetectionModel(label=self._categories[label_id], score=score, box=tuple(box))
            for box, label_id, score in detections
            if self._categories[label_id] in labels and score >= score_threshold
        )
