from data_platform.model import Dataset
from data_platform.dataset.house_config import HOUSE_DATASET
from data_platform.dataset.sale_config import SALE_DATASET

registry: dict[str, Dataset] = {
    SALE_DATASET.name.lower(): SALE_DATASET,
    HOUSE_DATASET.name.lower(): HOUSE_DATASET,
}


def get_dataset(name: str) -> Dataset:
    key = name.lower()
    if key not in registry:
        raise ValueError(f"Unsupported dataset: {name}")
    return registry[key]
