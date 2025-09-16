import itertools
import math
from typing import List, Any


def permutations(n, r):
    """Calculate the number of permutations for n items taken r at a time.

    Args:
        n (int): Total number of items
        r (int): Number of items to select

    Returns:
        int: Number of permutations, or 0 if invalid input

    Example:
        >>> permutations(3, 2)
        6 # Possible arrangements: (1,2), (1,3), (2,1), (2,3), (3,1), (3,2)
    """
    if n < 0 or r < 0 or r > n:
        return 0
    return math.factorial(n) // math.factorial(n - r)


def list_permutations(array: List[Any], r):
    """Generate all possible permutations of r elements from the given array.

    Args:
        array (List[Any]): Input array of elements
        r (int): Number of elements to select

    Returns:
        List[tuple]: List of all possible permutations, empty list if invalid input

    Example:
        >>> list_permutations([1, 2, 3], 2)
        [(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)]
    """
    if len(array) == 0 or r <= 0 or r > len(array):
        return []
    return list(itertools.permutations(array, r))


def combinations(n, r):
    """Calculate the number of combinations for n items taken r at a time.

    Args:
        n (int): Total number of items
        r (int): Number of items to select

    Returns:
        int: Number of combinations, or 0 if invalid input

    Example:
        >>> combinations(3, 2)
        3 # Possible combinations: (1,2), (1,3), (2,3)
    """
    if n < 0 or r < 0 or r > n:
        return 0
    return math.comb(n, r)


def list_combinations(array: List[Any], r):
    """Generate all possible combinations of r elements from the given array.

    Args:
        array (List[Any]): Input array of elements
        r (int): Number of elements to select

    Returns:
        List[tuple]: List of all possible combinations, empty list if invalid input

    Example:
        >>> list_combinations([1, 2, 3], 2)
        [(1, 2), (1, 3), (2, 3)]
    """
    if len(array) == 0 or r <= 0 or r > len(array):
        return []
    return list(itertools.combinations(array, r))


def distribute_objects_into_boxes(n_objects, n_boxes):
    """Calculate the number of ways to distribute distinct objects into distinct boxes.

    Args:
        n_objects (int): Number of objects to distribute
        n_boxes (int): Number of available boxes

    Returns:
        int: Number of possible distributions, or 0, if invalid input

    Example:
        >>> distribute_objects_into_boxes(2, 3)
        9 # Each object can go to any of the 3 boxes independently
    """
    if n_objects < 0 or n_boxes <= 0:
        return 0
    return n_boxes ** n_objects


def list_distributions(objects: List[Any], n_boxes):
    """Generate all possible distributions of objects into distinct boxes.

    Args:
        objects (List[Any]): List of objects to distribute
        n_boxes (int): Number of available boxes

    Returns:
        List[tuple]: List of all possible distributions where each number represents
                     the box index for a corresponding object, empty list if invalid input

    Example:
        >>> list_distributions([1, 2], 2)
        [(0, 0), (0, 1), (1, 0), (1, 1)] # Each number represents the box index
    """
    if len(objects) == 0 or n_boxes <= 0:
        return []

    box_indices = list(range(n_boxes))
    all_assignments = list(itertools.product(box_indices, repeat=len(objects)))

    return all_assignments
