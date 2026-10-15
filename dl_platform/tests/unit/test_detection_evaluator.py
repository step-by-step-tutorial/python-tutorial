import json
from pathlib import Path

import pytest

from conftest import make_detector, make_settings, write_images
from dl_platform.config.detection_tasks import VEHICLE_DETECTION
from dl_platform.evaluation import detection_evaluator
from dl_platform.evaluation.detection_evaluator import DetectionEvaluator
from dl_platform.util.csv_utils import read_rows

CATEGORIES = [{"id": 1, "name": "person"}, {"id": 2, "name": "bicycle"}, {"id": 3, "name": "car"},
              {"id": 4, "name": "motorcycle"}, {"id": 6, "name": "bus"}, {"id": 8, "name": "truck"}]


def write_coco(coco_dir: Path) -> None:
    """Three labelled images: a car where the fake detector finds one, a bicycle it misses, and a person only."""
    images = [{"id": image_id, "file_name": f"{image_id:012d}.jpg", "width": 64, "height": 48,
               "coco_url": f"http://images.cocodataset.org/val2017/{image_id:012d}.jpg"} for image_id in (1, 2, 3)]
    annotations = [
        {"id": 1, "image_id": 1, "category_id": 3, "bbox": [1, 1, 19, 19], "area": 361, "iscrowd": 0},
        {"id": 2, "image_id": 2, "category_id": 2, "bbox": [30, 20, 20, 20], "area": 400, "iscrowd": 0},
        {"id": 3, "image_id": 3, "category_id": 1, "bbox": [5, 5, 10, 10], "area": 100, "iscrowd": 0},
    ]
    path = coco_dir / "annotations" / "instances_val2017.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"images": images, "annotations": annotations, "categories": CATEGORIES}))
    write_images(coco_dir / "val2017", *(image["file_name"] for image in images))


@pytest.fixture
def coco_settings(tmp_path):
    settings = make_settings(tmp_path, coco_dir=tmp_path / "coco")
    write_coco(settings.coco_path)
    return settings


@pytest.fixture(autouse=True)
def fake_detector(mocker):
    detector = make_detector(boxes=[[1, 1, 20, 20]], labels=[3], scores=[0.9])
    return mocker.patch.object(detection_evaluator, "create_detector", return_value=detector)


def test_evaluate_scores_each_label_on_the_images_that_hold_task_labels(coco_settings) -> None:
    evaluator = DetectionEvaluator(coco_settings)

    results = {result.label: result for result in evaluator.evaluate()}

    assert results["all"].images == 2
    assert results["all"].objects == 2
    assert results["car"].ap == pytest.approx(1.0)
    assert results["car"].ar == pytest.approx(1.0)
    assert results["bicycle"].ap == 0
    assert results["all"].ap == pytest.approx(0.5)
    assert results["bus"].objects == 0
    rows = read_rows(coco_settings.evaluation_path)
    assert [row["label"] for row in rows] == ["all", *VEHICLE_DETECTION.labels]
    steps = [row["step"] for row in read_rows(coco_settings.execution_log_path(evaluator._audit.run_id, "evaluate"))]
    assert steps == ["images_selected", "model_loaded", "objects_detected", "evaluation_saved"]


def test_evaluate_limits_the_number_of_images(tmp_path) -> None:
    settings = make_settings(tmp_path, coco_dir=tmp_path / "coco", evaluation_images=1)
    write_coco(settings.coco_path)

    results = DetectionEvaluator(settings).evaluate()

    assert results[0].images == 1
    assert results[0].ap == pytest.approx(1.0)


def test_evaluate_scores_zero_when_nothing_is_detected(coco_settings, fake_detector) -> None:
    fake_detector.return_value = make_detector(boxes=[], labels=[], scores=[])

    results = DetectionEvaluator(coco_settings).evaluate()

    assert all(result.ap == 0 and result.ar == 0 for result in results)


def test_evaluate_requires_the_coco_annotations(tmp_path) -> None:
    with pytest.raises(FileNotFoundError, match="instances_val2017.json"):
        DetectionEvaluator(make_settings(tmp_path, coco_dir=tmp_path / "coco")).evaluate()
