import logging
from collections import Counter

from dl_platform.audit.audit_service import AuditService
from dl_platform.detector.detector_factory import create_detector
from dl_platform.model.image_detections_model import ImageDetectionsModel
from dl_platform.model.settings_model import SettingsModel
from dl_platform.repository.detection_repository import DetectionRepository
from dl_platform.repository.image_repository import ImageRepository
from dl_platform.visualize.detection_visualizer import DetectionVisualizer

logger = logging.getLogger(__name__)


class DetectionRunner:
    def __init__(self, settings: SettingsModel) -> None:
        self._settings = settings
        self._audit = AuditService(settings)
        self._image_repository = ImageRepository()
        self._detection_repository = DetectionRepository()
        self._visualizer = DetectionVisualizer(settings.task.labels)

    def run(self) -> tuple[ImageDetectionsModel, ...]:
        settings = self._settings
        task = settings.task
        logger.info("Detection started: task=%s run_id=%s model_type=%s", task.name, self._audit.run_id,
                    settings.model_type)

        detector = create_detector(settings.model_type, settings.model_dir, settings.device)
        self._audit.log_step("model_loaded", details=settings.model_type)

        paths = self._image_repository.find_all(settings.input_dir)
        self._audit.log_step("images_found", rows=len(paths), details=str(settings.input_dir))

        results = []
        for path in paths:
            image = self._image_repository.load(path)
            detections = detector.detect(image, task.labels, settings.score_threshold)
            self._image_repository.save(settings.annotated_dir / path.name, self._visualizer.render(image, detections))
            logger.info("Detected objects: image=%s objects=%s", path.name, len(detections))
            results.append(ImageDetectionsModel(path, detections))

        counts = ImageDetectionsModel.count_by_label(results)
        self._audit.log_step("objects_detected", rows=counts.total(), details=_format_counts(counts))

        self._detection_repository.save(settings.detections_path, results)
        self._audit.log_step("detections_saved", rows=counts.total(), details=str(settings.detections_path))
        logger.info("Detection completed: task=%s images=%s objects=%s %s output=%s", task.name, len(results),
                    counts.total(), _format_counts(counts), settings.annotated_dir)
        return tuple(results)


def _format_counts(counts: Counter[str]) -> str:
    return " ".join(f"{label}={count}" for label, count in counts.most_common())
