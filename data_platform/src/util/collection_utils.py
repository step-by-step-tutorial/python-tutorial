from collections.abc import Mapping

def list_of_values(map: Mapping) -> list[str]:
    return [str(item) for item in map.values()]