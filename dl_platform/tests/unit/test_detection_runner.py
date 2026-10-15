import pytest

from conftest import make_detector, make_settings, write_images
from dl_platform.inference import detection_runner
from dl_platform.inference.detection_runner import DetectionRunner
from dl_platform.util.csv_utils import read_rows


@pytest.fixture(autouse=True)
def fake_detector(mocker):
    detector = make_detector(boxes=[[1, 1, 20, 20], [2, 2, 30, 30]], labels=[3, 1], scores=[0.9, 0.8])
    return mocker.patch.object(detection_runner, "create_detector", return_value=detector)


def test_run_saves_annotated_images_detections_and_execution_log(vehicle_settings) -> None:
    runner = DetectionRunner(vehicle_settings)

    results = runner.run()

    assert [result.image_path.name for result in results] == ["parking.png", "street.jpg"]
    assert (vehicle_settings.annotated_dir / "parking.png").exists()
    assert (vehicle_settings.annotated_dir / "street.jpg").exists()
    rows = read_rows(vehicle_settings.detections_path)
    assert [(row["image"], row["label"]) for row in rows] == [("parking.png", "car"), ("street.jpg", "car")]
    steps = [row["step"] for row in read_rows(vehicle_settings.execution_log_path(runner._audit.run_id))]
    assert steps == ["model_loaded", "images_found", "objects_detected", "detections_saved"]


def test_run_without_execution_log_writes_no_audit(tmp_path) -> None:
    settings = make_settings(tmp_path, execution_log_enabled=False)
    write_images(settings.input_dir, "street.jpg")

    DetectionRunner(settings).run()

    assert not settings.audit_dir.exists()


def test_run_requires_the_task_image_folder(tmp_path) -> None:
    with pytest.raises(FileNotFoundError, match="vehicle_detection"):
        DetectionRunner(make_settings(tmp_path)).run()
