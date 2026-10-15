from pathlib import Path

from dl_platform.config.detection_tasks import PERSON_DETECTION
from dl_platform.config.model_type import ModelType
from dl_platform.model.settings_model import SettingsModel


def test_defaults_are_read_from_the_project_root() -> None:
    settings = SettingsModel.from_env(PERSON_DETECTION, environ={"PROJECT_ROOT": "/project"})

    assert settings.input_dir == Path("/project/data/person_detection")
    assert settings.model_dir == Path("/project/models")
    assert settings.annotated_dir == Path("/project/output/person_detection")
    assert settings.detections_path == Path("/project/output/person_detection_detections.csv")
    assert settings.execution_log_path("run") == Path("/project/audit_log/person_detection_detect_run.csv")
    assert settings.coco_path == Path("/project/data/coco")
    assert settings.evaluation_path == Path("/project/output/person_detection_evaluation.csv")
    assert settings.evaluation_images == 100
    assert settings.model_type == ModelType.FASTER_RCNN_MOBILENET
    assert settings.score_threshold == PERSON_DETECTION.score_threshold
    assert settings.execution_log_enabled


def test_environment_overrides_the_defaults() -> None:
    settings = SettingsModel.from_env(PERSON_DETECTION, environ={
        "DL_PLATFORM_DATA_DIR": "/images",
        "DL_PLATFORM_MODEL_TYPE": "faster_rcnn_resnet50",
        "DL_PLATFORM_DEVICE": "cuda",
        "DL_PLATFORM_SCORE_THRESHOLD": "0.8",
        "EXECUTION_LOG_ENABLED": "false",
        "DL_PLATFORM_COCO_DIR": "/coco",
        "DL_PLATFORM_EVALUATION_IMAGES": "20",
    })

    assert settings.input_dir == Path("/images/person_detection")
    assert settings.model_type == ModelType.FASTER_RCNN_RESNET50
    assert settings.device == "cuda"
    assert settings.score_threshold == 0.8
    assert not settings.execution_log_enabled
    assert settings.coco_path == Path("/coco")
    assert settings.evaluation_images == 20
