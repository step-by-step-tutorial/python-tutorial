import atexit
from typing import Any

from data_platform.registry.registry import Registry


class ConnectionRegistry(Registry[Any]):
    def __init__(self) -> None:
        super().__init__("connection")

    def close(self, name: str) -> None:
        if not self.contains(name):
            return

        connection = self.get_item(name)
        self.remove(name)

        if hasattr(connection, "flush") and callable(connection.flush):
            connection.flush()
        if hasattr(connection, "dispose") and callable(connection.dispose):
            connection.dispose()
        elif hasattr(connection, "close") and callable(connection.close):
            connection.close()

    def close_all(self) -> None:
        for name in self.loaded_names():
            self.close(name)


connection_registry = ConnectionRegistry()

atexit.register(connection_registry.close_all)
