from dataset.definition import Dataset
from dataset.house.config import HOUSE_DATASET
from dataset.sale.config import SALE_DATASET

registry: dict[str, Dataset] = {
    SALE_DATASET.name.lower(): SALE_DATASET,
    HOUSE_DATASET.name.lower(): HOUSE_DATASET,
}


def get_dataset(name: str) -> Dataset:
    key = name.lower()
    if key not in registry:
        raise ValueError(f"Unsupported dataset: {name}")
    return registry[key]
