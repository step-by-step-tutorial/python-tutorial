from conftest import make_image
from dl_platform.config.model_type import ModelType
from dl_platform.detector.detector_factory import create_detector


def test_create_detector_builds_an_untrained_coco_detector(tmp_path) -> None:
    detector = create_detector(ModelType.FASTER_RCNN_MOBILENET, tmp_path, pretrained=False)

    assert len(detector.categories) == 91
    assert detector.categories[1] == "person"
    assert isinstance(detector.detect(make_image(), labels=("car",), score_threshold=0.0), tuple)
