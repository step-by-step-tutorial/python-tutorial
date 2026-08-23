from collections.abc import Callable
from typing import Generic, TypeVar


RegistryItem = TypeVar("RegistryItem")


class Registry(Generic[RegistryItem]):
    def __init__(self, registry_name: str, key_transform: Callable[[str], str]  = (lambda key: key)) -> None:
        self.registry_name = registry_name
        self.key_transform = key_transform
        self.items: dict[str, RegistryItem] = {}
        self.lazy_item: dict[str, tuple[Callable[[], RegistryItem], bool]] = {}

    def register(self, name: str, item: RegistryItem) -> None:
        key = self.key_transform(name)
        if key in self.items:
            raise ValueError(f"{self.registry_name.capitalize()} is already registered: {name}")
        self.items[key] = item

    def register_lazy_item(self, name: str, lazy_function: Callable[[], RegistryItem], cache: bool = True) -> None:
        key = self.key_transform(name)
        if key in self.items or key in self.lazy_item:
            raise ValueError(f"{self.registry_name.capitalize()} is already registered: {name}")
        self.lazy_item[key] = (lazy_function, cache)

    def get_item(self, name: str) -> RegistryItem:
        key = self.key_transform(name)

        if key in self.items:
            return self.items[key]
        if key in self.lazy_item:
            lazy_function, should_cache = self.lazy_item[key]
            item = lazy_function()
            if should_cache:
                self.register(key, item)
            return item

        raise ValueError(f"Unsupported {self.registry_name}: {name}")

    def contains(self, name: str) -> bool:
        return self.key_transform(name) in self.items or self.key_transform(name) in self.lazy_item

    def remove(self, name: str) -> None:
        if name in self.items:
            self.items.pop(self.key_transform(name), None)
        elif name in self.lazy_item:
            self.lazy_item.pop(self.key_transform(name), None)

    def names(self) -> tuple[str, ...]:
        return tuple(self.items)

    def clear(self) -> None:
        self.items.clear()
        self.lazy_item.clear()
