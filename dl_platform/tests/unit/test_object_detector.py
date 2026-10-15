from conftest import make_detector, make_image
from dl_platform.model.detection_model import DetectionModel


def test_detect_keeps_requested_labels_above_the_threshold() -> None:
    detector = make_detector(
        boxes=[[1, 2, 10, 20], [5, 5, 15, 15], [0, 0, 8, 8], [3, 3, 9, 9]],
        labels=[3, 1, 2, 4],
        scores=[0.9, 0.95, 0.3, 0.99],
    )

    detections = detector.detect(make_image(), labels=("car", "bicycle"), score_threshold=0.5)

    assert detections == (DetectionModel(label="car", score=detections[0].score, box=(1.0, 2.0, 10.0, 20.0)),)
    assert round(detections[0].score, 2) == 0.9


def test_detect_returns_nothing_without_matches() -> None:
    detector = make_detector(boxes=[], labels=[], scores=[])

    assert detector.detect(make_image(), labels=("car",), score_threshold=0.5) == ()
