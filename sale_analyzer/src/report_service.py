import pandas as pd

from analyzer_service import (
    get_total_revenue,
    get_average_order_value,
    get_revenue_by_category,
    get_revenue_by_country,
    get_top_products_by_quantity,
)


def build_report(df: pd.DataFrame) -> str:
    report = []

    report.append("Sales Data Analysis Report")
    report.append("=" * 40)

    report.append(f"Total Revenue: {get_total_revenue(df):.2f}")
    report.append(f"Average Order Value: {get_average_order_value(df):.2f}")

    report.append("")
    report.append("Revenue by Category:")
    report.append(str(get_revenue_by_category(df)))

    report.append("")
    report.append("Revenue by Country:")
    report.append(str(get_revenue_by_country(df)))

    report.append("")
    report.append("Top Products by Quantity:")
    report.append(str(get_top_products_by_quantity(df)))

    return "\n".join(report)
