from test_data.util.collection_utils import topological_sort


def test_topological_sort_places_dependencies_first() -> None:
    order = topological_sort(
        {
            "email": ("first_name", "last_name"),
            "first_name": (),
            "last_name": (),
        }
    )

    assert order.index("first_name") < order.index("email")
    assert order.index("last_name") < order.index("email")
