from data_platform.model.event_converter import EventConverter
from data_platform.registry.base_registry import Registry


class EventConverterRegistry(Registry[EventConverter]):
    def __init__(self) -> None:
        super().__init__("event converter", str.lower)


event_converter_registry = EventConverterRegistry()

