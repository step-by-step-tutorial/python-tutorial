import ast

import pytest

from test_data.util.formula_utils import check_formula, evaluate_formula


def parse(formula: str) -> ast.expr:
    return ast.parse(formula, mode="eval").body


def test_evaluate_formula_supports_arithmetic_over_values() -> None:
    expression = parse("values[0] - values[0] * values[1] / 100 + values[2] + -values[3] ** 2 % 5")
    check_formula(expression, 4)

    assert evaluate_formula(expression, [200.0, 10.0, 5.0, 2.0]) == 200 - 20 + 5 + (-(2.0 ** 2) % 5)


@pytest.mark.parametrize(
    "formula",
    [
        "__import__('os').system('echo')",
        "values.__class__",
        "values[4]",
        "values[-1]",
        "abs(values[0])",
        "True + 1",
        "'a' * 3",
        "values[0] if values[1] else 0",
    ],
)
def test_check_formula_rejects_anything_but_arithmetic(formula: str) -> None:
    with pytest.raises(ValueError):
        check_formula(parse(formula), 4)
