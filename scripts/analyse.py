import pandas as pd
from clean import load_and_clean


def top_items_by_revenue(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return (
        df.groupby("menu_item")["total_price"]
        .sum()
        .sort_values(ascending=False)
        .head(n)
        .reset_index()
        .rename(columns={"total_price": "revenue"})
    )


def top_items_by_quantity(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return (
        df.groupby("menu_item")["quantity"]
        .sum()
        .sort_values(ascending=False)
        .head(n)
        .reset_index()
    )


def sales_by_hour(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("hour")
        .agg(orders=("order_id", "count"), revenue=("total_price", "sum"))
        .reset_index()
    )


def sales_by_day(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("day_of_week", observed=True)
        .agg(orders=("order_id", "count"), revenue=("total_price", "sum"))
        .reset_index()
    )


def monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("month")["total_price"]
        .sum()
        .reset_index()
        .rename(columns={"total_price": "revenue"})
    )


def revenue_by_category(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("category")["total_price"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"total_price": "revenue"})
    )


def server_performance(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("server")
        .agg(orders=("order_id", "count"), revenue=("total_price", "sum"))
        .sort_values("revenue", ascending=False)
        .reset_index()
    )


def payment_split(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("payment_method")["total_price"]
        .sum()
        .reset_index()
        .rename(columns={"total_price": "revenue"})
    )


if __name__ == "__main__":
    df = load_and_clean()

    print("\n=== Top 5 items by revenue ===")
    print(top_items_by_revenue(df, 5).to_string(index=False))

    print("\n=== Busiest hours ===")
    print(sales_by_hour(df).sort_values("revenue", ascending=False).head(5).to_string(index=False))

    print("\n=== Revenue by day ===")
    print(sales_by_day(df).to_string(index=False))

    print("\n=== Server performance ===")
    print(server_performance(df).to_string(index=False))
