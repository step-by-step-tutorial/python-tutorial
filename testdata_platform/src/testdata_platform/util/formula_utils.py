import ast
import operator

FORMULA_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def check_formula(node: ast.expr, value_count: int) -> None:
    """Allow only numbers, values[<index>] and arithmetic operators, so a formula cannot run code."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return
    if isinstance(node, ast.BinOp) and type(node.op) in FORMULA_OPERATORS:
        check_formula(node.left, value_count)
        check_formula(node.right, value_count)
        return
    if isinstance(node, ast.UnaryOp) and type(node.op) in FORMULA_OPERATORS:
        check_formula(node.operand, value_count)
        return
    if (isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) and node.value.id == "values"
            and isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, int)
            and 0 <= node.slice.value < value_count):
        return
    raise ValueError(f"unsupported expression '{ast.unparse(node)}'")


def evaluate_formula(node: ast.expr, values: list[float]) -> float:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        return FORMULA_OPERATORS[type(node.op)](evaluate_formula(node.left, values), evaluate_formula(node.right, values))
    if isinstance(node, ast.UnaryOp):
        return FORMULA_OPERATORS[type(node.op)](evaluate_formula(node.operand, values))
    return values[node.slice.value]  # values[<index>], validated by check_formula


def format_number(value: float) -> str:
    """Write a whole-number result as an integer (3, not 3.0) so integer columns stay integers."""
    return str(int(value)) if float(value).is_integer() else str(value)
