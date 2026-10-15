import contextlib
import io
import logging
import urllib.request
from collections.abc import Sequence
from pathlib import Path

from pycocotools.coco import COCO

logger = logging.getLogger(__name__)

ANNOTATIONS_FILE = "annotations/instances_val2017.json"
IMAGES_FOLDER = "val2017"


class CocoRepository:
    """Reads the COCO val2017 annotations and downloads only the images an evaluation needs."""

    def __init__(self, coco_dir: Path) -> None:
        self._coco_dir = coco_dir
        annotations_path = coco_dir / ANNOTATIONS_FILE
        if not annotations_path.is_file():
            raise FileNotFoundError(f"COCO annotations not found: {annotations_path}")
        with contextlib.redirect_stdout(io.StringIO()):
            self.coco = COCO(str(annotations_path))
        logger.info("Loaded COCO annotations: path=%s images=%s", annotations_path, len(self.coco.imgs))

    def category_ids(self, labels: Sequence[str]) -> dict[str, int]:
        ids = {category["name"]: category["id"] for category in self.coco.loadCats(self.coco.getCatIds())}
        missing = [label for label in labels if label not in ids]
        if missing:
            raise ValueError(f"Labels are not COCO categories: {missing}")
        return {label: ids[label] for label in labels}

    def find_image_ids(self, category_ids: Sequence[int], limit: int) -> list[int]:
        """Return the first images, by id, that hold at least one object of the categories."""
        annotation_ids = self.coco.getAnnIds(catIds=list(category_ids), iscrowd=False)
        image_ids = sorted({annotation["image_id"] for annotation in self.coco.loadAnns(annotation_ids)})
        return image_ids[:limit]

    def count_objects(self, image_ids: Sequence[int], category_ids: Sequence[int]) -> int:
        return len(self.coco.getAnnIds(imgIds=list(image_ids), catIds=list(category_ids), iscrowd=False))

    def image_path(self, image_id: int) -> Path:
        image = self.coco.imgs[image_id]
        path = self._coco_dir / IMAGES_FOLDER / image["file_name"]
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(image["coco_url"], path)
            logger.info("Downloaded COCO image: %s", path.name)
        return path
