from dataset.definition import Dataset


def get_dataset(name: str) -> Dataset:
    from dataset.registry import get_dataset as _get_dataset
    return _get_dataset(name)


def get_dataset_names() -> tuple[str, ...]:
    from dataset.registry import get_dataset_names as _get_dataset_names
    return _get_dataset_names()


__all__ = ["Dataset", "get_dataset", "get_dataset_names"]
