import contextlib
import io
import logging
from collections.abc import Sequence

import numpy as np
from pycocotools.cocoeval import COCOeval

from dl_platform.audit.audit_service import AuditService
from dl_platform.config.operation import Operation
from dl_platform.detector.detector_factory import create_detector
from dl_platform.model.detection_model import DetectionModel
from dl_platform.model.evaluation_model import ALL_LABELS, EvaluationModel
from dl_platform.model.settings_model import SettingsModel
from dl_platform.repository.coco_repository import CocoRepository
from dl_platform.repository.evaluation_repository import EvaluationRepository
from dl_platform.repository.image_repository import ImageRepository

logger = logging.getLogger(__name__)

# Keep every detection the model returns, so the precision-recall curve covers all scores.
EVALUATION_SCORE_THRESHOLD = 0.0
# Indexes into COCOeval precision and recall: IoU 0.50, all object areas, up to 100 detections per image.
IOU_50 = 0
ALL_AREAS = 0
MAX_DETECTIONS = 2


class DetectionEvaluator:
    """Measures how well the task detects its labels on labelled COCO val2017 images."""

    def __init__(self, settings: SettingsModel) -> None:
        self._settings = settings
        self._audit = AuditService(settings, Operation.EVALUATE)
        self._image_repository = ImageRepository()
        self._evaluation_repository = EvaluationRepository()

    def evaluate(self) -> tuple[EvaluationModel, ...]:
        settings = self._settings
        task = settings.task
        logger.info("Evaluation started: task=%s run_id=%s model_type=%s", task.name, self._audit.run_id,
                    settings.model_type)

        coco_repository = CocoRepository(settings.coco_path)
        category_ids = coco_repository.category_ids(task.labels)
        image_ids = coco_repository.find_image_ids(list(category_ids.values()), settings.evaluation_images)
        objects = coco_repository.count_objects(image_ids, list(category_ids.values()))
        self._audit.log_step("images_selected", rows=len(image_ids), details=f"objects={objects}")

        detector = create_detector(settings.model_type, settings.model_dir, settings.device)
        self._audit.log_step("model_loaded", details=settings.model_type)

        predictions = []
        for index, image_id in enumerate(image_ids, start=1):
            image = self._image_repository.load(coco_repository.image_path(image_id))
            detections = detector.detect(image, task.labels, EVALUATION_SCORE_THRESHOLD)
            predictions.extend(_to_coco_results(image_id, detections, category_ids))
            if index % 25 == 0 or index == len(image_ids):
                logger.info("Evaluated images: %s/%s", index, len(image_ids))
        self._audit.log_step("objects_detected", rows=len(predictions))

        results = self._score(coco_repository, image_ids, category_ids, predictions)
        self._evaluation_repository.save(settings.evaluation_path, results)
        self._audit.log_step("evaluation_saved", rows=len(results), details=str(settings.evaluation_path))
        overall = results[0]
        logger.info("Evaluation completed: task=%s images=%s objects=%s AP=%.3f AP50=%.3f AR=%.3f output=%s",
                    task.name, overall.images, overall.objects, overall.ap, overall.ap50, overall.ar,
                    settings.evaluation_path)
        return results

    def _score(
            self,
            coco_repository: CocoRepository,
            image_ids: Sequence[int],
            category_ids: dict[str, int],
            predictions: list[dict],
    ) -> tuple[EvaluationModel, ...]:
        """Score all labels together, then each label alone, with the COCO average precision and recall."""
        coco = coco_repository.coco
        # precision: [iou, recall, category, area, max detections]; recall: [iou, category, area, max detections]
        precision = np.zeros((1, 1, len(category_ids)))
        recall = np.zeros((1, len(category_ids)))
        # loadRes cannot read an empty result list, so a model that found nothing keeps the zero scores.
        if predictions:
            with contextlib.redirect_stdout(io.StringIO()):
                evaluation = COCOeval(coco, coco.loadRes(predictions), "bbox")
                evaluation.params.imgIds = list(image_ids)
                evaluation.params.catIds = list(category_ids.values())
                evaluation.evaluate()
                evaluation.accumulate()
            precision = evaluation.eval["precision"][:, :, :, ALL_AREAS, MAX_DETECTIONS]
            recall = evaluation.eval["recall"][:, :, ALL_AREAS, MAX_DETECTIONS]

        groups = [(ALL_LABELS, slice(None))] + [(label, slice(index, index + 1))
                                               for index, label in enumerate(category_ids)]
        return tuple(
            EvaluationModel(
                label=label,
                images=len(image_ids),
                objects=coco_repository.count_objects(image_ids, list(category_ids.values())[categories]),
                ap=_mean(precision[:, :, categories]),
                ap50=_mean(precision[IOU_50, :, categories]),
                ar=_mean(recall[:, categories]),
            )
            for label, categories in groups
        )


def _to_coco_results(image_id: int, detections: Sequence[DetectionModel], category_ids: dict[str, int]) -> list[dict]:
    results = []
    for detection in detections:
        x_min, y_min, x_max, y_max = detection.box
        results.append({
            "image_id": image_id,
            "category_id": category_ids[detection.label],
            "bbox": [x_min, y_min, x_max - x_min, y_max - y_min],
            "score": detection.score,
        })
    return results


def _mean(values: np.ndarray) -> float:
    """Average the values COCOeval measured; -1 marks a category with no objects in the images."""
    measured = values[values > -1]
    return float(measured.mean()) if measured.size else 0.0
