import logging
from pathlib import Path

from PIL import Image
from torch import Tensor
from torchvision.transforms.functional import pil_to_tensor, to_pil_image

logger = logging.getLogger(__name__)

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}


class ImageRepository:

    def find_all(self, directory: Path) -> list[Path]:
        if not directory.is_dir():
            raise FileNotFoundError(f"Image folder not found: {directory}")
        paths = sorted(path for path in directory.iterdir() if path.suffix.lower() in IMAGE_SUFFIXES)
        if not paths:
            raise ValueError(f"No .jpg, .jpeg or .png images found in {directory}")
        logger.info("Found images: folder=%s images=%s", directory, len(paths))
        return paths

    def load(self, path: Path) -> Tensor:
        with Image.open(path) as image:
            return pil_to_tensor(image.convert("RGB"))

    def save(self, path: Path, image: Tensor) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        to_pil_image(image).save(path)
        return path
