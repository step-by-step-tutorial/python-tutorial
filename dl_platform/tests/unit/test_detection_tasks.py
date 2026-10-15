import pytest

from dl_platform.config.detection_tasks import DETECTION_TASKS
from dl_platform.config.model_type import ModelType
from dl_platform.detector.detector_factory import DETECTORS


@pytest.mark.parametrize("model_type", list(ModelType))
@pytest.mark.parametrize("task", list(DETECTION_TASKS.values()), ids=list(DETECTION_TASKS))
def test_every_task_label_is_a_detector_category(task, model_type) -> None:
    _, weights = DETECTORS[model_type]

    assert set(task.labels) <= set(weights.meta["categories"])
