import logging
from collections.abc import Callable
from typing import Generic, TypeVar

RegistryItem = TypeVar("RegistryItem")
logger = logging.getLogger(__name__)


class Registry(Generic[RegistryItem]):
    def __init__(self, registry_name: str, key_transform: Callable[[str], str] = (lambda key: key)) -> None:
        self._registry_name = registry_name
        self._key_transform = key_transform
        self._items: dict[str, RegistryItem] = {}
        self._lazy_loading_items: dict[str, tuple[Callable[[], RegistryItem], bool]] = {}

    def register(self, name: str, item: RegistryItem) -> None:
        key = self._key_transform(name)
        if key in self._items:
            raise ValueError(f"{self._registry_name.capitalize()} is already registered: {name}")
        self._items[key] = item
        logger.info("Registered %s: %s", self._registry_name, name)

    def register_lazy_item(self, name: str, lazy_function: Callable[[], RegistryItem], cache: bool = True) -> None:
        key = self._key_transform(name)
        if key in self._items or key in self._lazy_loading_items:
            raise ValueError(f"{self._registry_name.capitalize()} is already registered: {name}")
        self._lazy_loading_items[key] = (lazy_function, cache)
        logger.info("Registered lazy %s: %s", self._registry_name, name)

    def get_item(self, name: str) -> RegistryItem:
        key = self._key_transform(name)

        if key in self._items:
            logger.debug("Retrieved %s: %s", self._registry_name, name)
            return self._items[key]
        if key in self._lazy_loading_items:
            logger.info("Lazy loading %s: %s", self._registry_name, name)
            lazy_function, should_cache = self._lazy_loading_items[key]
            item = lazy_function()
            if should_cache:
                self.register(key, item)
            return item

        raise ValueError(f"Unsupported {self._registry_name}: {name}")

    def contains(self, name: str) -> bool:
        key = self._key_transform(name)
        return key in self._items or key in self._lazy_loading_items

    def remove(self, name: str) -> None:
        key = self._key_transform(name)
        if key in self._items:
            self._items.pop(key)
            logger.info("Removed %s: %s", self._registry_name, name)
        elif key in self._lazy_loading_items:
            self._lazy_loading_items.pop(key)
            logger.info("Removed lazy %s: %s", self._registry_name, name)

    def names(self) -> tuple[str, ...]:
        return tuple((*self._items, *self._lazy_loading_items))

    def loaded_names(self) -> tuple[str, ...]:
        return tuple(self._items)

    def clear(self) -> None:
        self._items.clear()
        self._lazy_loading_items.clear()
