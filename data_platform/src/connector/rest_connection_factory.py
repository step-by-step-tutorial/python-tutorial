from __future__ import annotations

import atexit
from typing import Any
from urllib.request import build_opener

registry: dict[str, Any] = {}

def create_sale_connection():
    return build_opener()


def create_house_connection():
    return build_opener()


registry["sale.rest"] = create_sale_connection()
registry["house.rest"] = create_house_connection()


def get_connection(name: str):
    return registry[name]


def close_connection(name: str) -> None:
    registry.pop(name, None)


def close_all_connections() -> None:
    registry.clear()


atexit.register(close_all_connections)
