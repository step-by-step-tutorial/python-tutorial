from dl_platform.model.detection_task_model import DetectionTaskModel

# Labels are COCO category names, which the pre-trained detectors already recognize.
VEHICLE_DETECTION = DetectionTaskModel(
    name="vehicle_detection",
    labels=("bicycle", "car", "motorcycle", "bus", "truck"),
)

PERSON_DETECTION = DetectionTaskModel(
    name="person_detection",
    labels=("person",),
)

ANIMAL_DETECTION = DetectionTaskModel(
    name="animal_detection",
    labels=("bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe"),
)

DETECTION_TASKS: dict[str, DetectionTaskModel] = {
    task.name: task for task in (VEHICLE_DETECTION, PERSON_DETECTION, ANIMAL_DETECTION)
}
