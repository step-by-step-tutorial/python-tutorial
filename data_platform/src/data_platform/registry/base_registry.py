import logging
from collections.abc import Callable
from typing import Generic, TypeVar

RegistryItem = TypeVar("RegistryItem")
logger = logging.getLogger(__name__)


class Registry(Generic[RegistryItem]):
    def __init__(self, registry_name: str, key_transform: Callable[[str], str] = (lambda key: key)) -> None:
        self.registry_name = registry_name
        self.key_transform = key_transform
        self.items: dict[str, RegistryItem] = {}
        self.lazy_loading_items: dict[str, tuple[Callable[[], RegistryItem], bool]] = {}

    def register(self, name: str, item: RegistryItem) -> None:
        key = self.key_transform(name)
        if key in self.items:
            raise ValueError(f"{self.registry_name.capitalize()} is already registered: {name}")
        self.items[key] = item
        logger.info("Registered %s: %s", self.registry_name, name)

    def register_lazy_item(self, name: str, lazy_function: Callable[[], RegistryItem], cache: bool = True) -> None:
        key = self.key_transform(name)
        if key in self.items or key in self.lazy_loading_items:
            raise ValueError(f"{self.registry_name.capitalize()} is already registered: {name}")
        self.lazy_loading_items[key] = (lazy_function, cache)
        logger.info("Registered lazy %s: %s", self.registry_name, name)

    def get_item(self, name: str) -> RegistryItem:
        key = self.key_transform(name)

        if key in self.items:
            logger.debug("Retrieved %s: %s", self.registry_name, name)
            return self.items[key]
        if key in self.lazy_loading_items:
            logger.info("Lazy loading %s: %s", self.registry_name, name)
            lazy_function, should_cache = self.lazy_loading_items[key]
            item = lazy_function()
            if should_cache:
                self.register(key, item)
            return item

        raise ValueError(f"Unsupported {self.registry_name}: {name}")

    def contains(self, name: str) -> bool:
        key = self.key_transform(name)
        return key in self.items or key in self.lazy_loading_items

    def remove(self, name: str) -> None:
        key = self.key_transform(name)
        if key in self.items:
            self.items.pop(key)
            logger.info("Removed %s: %s", self.registry_name, name)
        elif key in self.lazy_loading_items:
            self.lazy_loading_items.pop(key)
            logger.info("Removed lazy %s: %s", self.registry_name, name)

    def names(self) -> tuple[str, ...]:
        return tuple((*self.items, *self.lazy_loading_items))

    def loaded_names(self) -> tuple[str, ...]:
        return tuple(self.items)

    def clear(self) -> None:
        self.items.clear()
        self.lazy_loading_items.clear()
