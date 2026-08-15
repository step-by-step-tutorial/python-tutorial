from dataset.definition import Dataset
from dataset.house.config import HOUSE_DATASET
from dataset.sale.config import SALE_DATASET

_DATASETS: dict[str, Dataset] = {
    SALE_DATASET.name.lower(): SALE_DATASET,
    HOUSE_DATASET.name.lower(): HOUSE_DATASET,
}


def get_dataset(name: str) -> Dataset:
    try:
        return _DATASETS[name.lower()]
    except KeyError as error:
        available_datasets = ", ".join(sorted(_DATASETS))
        raise ValueError(f"Unsupported dataset: {name}. Supported datasets: {available_datasets}") from error


def get_dataset_names() -> tuple[str, ...]:
    return tuple(sorted(_DATASETS))
