import pytest
import torch

from conftest import make_image, write_images
from dl_platform.repository.image_repository import ImageRepository


def test_find_all_returns_sorted_images_only(tmp_path) -> None:
    write_images(tmp_path, "b.png", "a.jpg", "c.JPEG")
    (tmp_path / "notes.txt").write_text("not an image", encoding="utf-8")

    assert [path.name for path in ImageRepository().find_all(tmp_path)] == ["a.jpg", "b.png", "c.JPEG"]


def test_find_all_requires_an_existing_folder(tmp_path) -> None:
    with pytest.raises(FileNotFoundError, match="Image folder not found"):
        ImageRepository().find_all(tmp_path / "missing")


def test_find_all_requires_images(tmp_path) -> None:
    with pytest.raises(ValueError, match="No .jpg, .jpeg or .png images"):
        ImageRepository().find_all(tmp_path)


def test_png_round_trip_keeps_the_pixels(tmp_path) -> None:
    repository = ImageRepository()
    image = make_image()

    loaded = repository.load(repository.save(tmp_path / "out" / "image.png", image))

    assert torch.equal(loaded, image)
