import logging
from collections.abc import Callable
from pathlib import Path

import torch
from torchvision.models import WeightsEnum
from torchvision.models.detection import (
    FasterRCNN,
    FasterRCNN_MobileNet_V3_Large_FPN_Weights,
    FasterRCNN_ResNet50_FPN_V2_Weights,
    fasterrcnn_mobilenet_v3_large_fpn,
    fasterrcnn_resnet50_fpn_v2,
)

from dl_platform.config.model_type import ModelType
from dl_platform.detector.object_detector import ObjectDetector

logger = logging.getLogger(__name__)

DETECTORS: dict[ModelType, tuple[Callable[..., FasterRCNN], WeightsEnum]] = {
    ModelType.FASTER_RCNN_MOBILENET: (
        fasterrcnn_mobilenet_v3_large_fpn,
        FasterRCNN_MobileNet_V3_Large_FPN_Weights.DEFAULT,
    ),
    ModelType.FASTER_RCNN_RESNET50: (
        fasterrcnn_resnet50_fpn_v2,
        FasterRCNN_ResNet50_FPN_V2_Weights.DEFAULT,
    ),
}


def create_detector(
        model_type: ModelType,
        model_dir: Path,
        device: str = "cpu",
        pretrained: bool = True,
) -> ObjectDetector:
    """Build a COCO detector; pre-trained weights are downloaded once into model_dir."""
    builder, weights = DETECTORS[model_type]
    categories = weights.meta["categories"]
    torch.hub.set_dir(str(model_dir))
    model = builder(
        weights=weights if pretrained else None,
        weights_backbone=None,
        num_classes=len(categories),
    )
    logger.info("Created detector: model_type=%s pretrained=%s device=%s", model_type, pretrained, device)
    return ObjectDetector(model, categories, weights.transforms(), device)
