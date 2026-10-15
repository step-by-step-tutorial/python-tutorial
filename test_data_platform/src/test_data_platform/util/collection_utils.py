from collections.abc import Hashable, Iterable, Mapping
from graphlib import TopologicalSorter
from typing import TypeVar

Node = TypeVar("Node", bound=Hashable)


def topological_sort(graph: Mapping[Node, Iterable[Node]]) -> tuple[Node, ...]:
    return tuple(TopologicalSorter(graph).static_order())
