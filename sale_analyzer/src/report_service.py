import pandas as pd

from analyzer_service import (
    get_total_revenue,
    get_average_order_value,
    get_revenue_by_category,
    get_revenue_by_country,
    get_top_products_by_quantity,
)

EMPTY_LINE = ""
SEPARATOR_LINE = "=" * 40


def build_sale_report(df: pd.DataFrame) -> str:
    report = [
        "sale Data Analysis Report",
        SEPARATOR_LINE,
        f"Total Revenue: {get_total_revenue(df):.2f}",
        f"Average Order Value: {get_average_order_value(df):.2f}",
        EMPTY_LINE,
        "Revenue by Category:",
        str(get_revenue_by_category(df)),
        EMPTY_LINE,
        "Revenue by Country:",
        str(get_revenue_by_country(df)),
        EMPTY_LINE,
        "Top Products by Quantity:",
        str(get_top_products_by_quantity(df)),
    ]

    return "\n".join(report)
