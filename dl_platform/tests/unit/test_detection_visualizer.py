import torch

from conftest import make_image
from dl_platform.model.detection_model import DetectionModel
from dl_platform.visualize.detection_visualizer import DetectionVisualizer


def test_render_draws_boxes_on_a_copy() -> None:
    image = torch.zeros((3, 40, 40), dtype=torch.uint8)

    rendered = DetectionVisualizer(("car",)).render(image, [DetectionModel("car", 0.9, (5, 5, 30, 30))])

    assert rendered.shape == image.shape
    assert rendered.dtype == torch.uint8
    assert rendered.any()
    assert not image.any()


def test_render_without_detections_returns_the_image() -> None:
    image = make_image()

    assert DetectionVisualizer(("car",)).render(image, []) is image
