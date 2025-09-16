import pytest

from statictic import (permutations, list_permutations,
                       combinations, list_combinations,
                       distribute_objects_into_boxes, list_distributions)


@pytest.mark.parametrize("given_n, given_r, expected", [
    (3, 3, 6),
    (2, 2, 2),
    (3, 2, 6),
    (2, 3, 0),
    (0, 1, 0),
    (1, 0, 1),
    (0, 0, 1),
    (-2, 1, 0),
    (2, -2, 0),
])
def test_permutations(given_n, given_r, expected):
    actual = permutations(given_n, given_r)
    assert actual == expected


@pytest.mark.parametrize("given_array, given_r, expected", [
    ([1, 2, 3], 3, [(1, 2, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 1, 2), (3, 2, 1)]),
    ([1, 2], 2, [(1, 2), (2, 1)]),
    ([1, 2, 3], 2, [(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)]),
    ([], 1, []),
    ([1], 0, []),
    ([], 0, []),
    ([1, 2], -1, []),
    ([1, 2], 3, []),
])
def test_permutations_array(given_array, given_r, expected):
    actual = list_permutations(given_array, given_r)
    assert actual == expected


@pytest.mark.parametrize("given_n, given_r, expected", [
    (5, 2, 10),
    (4, 2, 6),
    (3, 2, 3),
    (3, 3, 1),
    (2, 2, 1),
    (3, 0, 1),
    (0, 0, 1),
    (2, 3, 0),
    (0, 1, 0),
    (-2, 1, 0),
    (2, -1, 0),
])
def test_combinations(given_n, given_r, expected):
    actual = combinations(given_n, given_r)
    assert actual == expected


@pytest.mark.parametrize("given_array, given_r, expected", [
    ([1, 2, 3], 2, [(1, 2), (1, 3), (2, 3)]),
    ([1, 2, 3], 3, [(1, 2, 3)]),
    ([1, 2], 2, [(1, 2)]),
    ([1, 2], 1, [(1,), (2,)]),
    ([], 1, []),
    ([1], 0, []),
    ([], 0, []),
    ([1, 2], -1, []),
    ([1, 2], 3, []),
])
def test_combinations_array(given_array, given_r, expected):
    actual = list_combinations(given_array, given_r)
    assert actual == expected


@pytest.mark.parametrize("given_n_objects, given_n_boxes, expected", [
    (5, 3, 243),
    (3, 2, 8),
    (0, 3, 1),
    (3, 0, 0),
    (-1, 2, 0),
    (3, -2, 0),
])
def test_distribute_objects_into_boxes(given_n_objects, given_n_boxes, expected):
    actual = distribute_objects_into_boxes(given_n_objects, given_n_boxes)
    assert actual == expected


@pytest.mark.parametrize("given_objects, given_n_boxes, expected_length", [
    ([1, 2, 3], 2, 8),
    ([1, 2], 3, 9),
    ([], 3, 0),
    ([1], 0, 0),
    ([1, 2], -1, 0),
])
def test_list_distributions(given_objects, given_n_boxes, expected_length):
    actual = list_distributions(given_objects, given_n_boxes)
    assert len(actual) == expected_length
