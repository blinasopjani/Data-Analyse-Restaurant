import pandas as pd
from pathlib import Path
from clean import load_and_clean
from analyse import (
    top_items_by_revenue,
    top_items_by_quantity,
    sales_by_hour,
    sales_by_day,
    monthly_revenue,
    revenue_by_category,
    server_performance,
    payment_split,
)

OUTPUT_PATH = Path(__file__).parent.parent / "data" / "restaurant_report.xlsx"


def export(path: Path = OUTPUT_PATH) -> None:
    df = load_and_clean()

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        top_items_by_revenue(df).to_excel(writer, sheet_name="Top Items Revenue", index=False)
        top_items_by_quantity(df).to_excel(writer, sheet_name="Top Items Quantity", index=False)
        sales_by_hour(df).to_excel(writer, sheet_name="Sales by Hour", index=False)
        sales_by_day(df).to_excel(writer, sheet_name="Sales by Day", index=False)
        monthly_revenue(df).to_excel(writer, sheet_name="Monthly Revenue", index=False)
        revenue_by_category(df).to_excel(writer, sheet_name="By Category", index=False)
        server_performance(df).to_excel(writer, sheet_name="Server Performance", index=False)
        payment_split(df).to_excel(writer, sheet_name="Payment Split", index=False)

    print(f"Report saved to {path}")


if __name__ == "__main__":
    export()
