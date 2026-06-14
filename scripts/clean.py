import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "restaurant_sales.csv"


def load_and_clean(path: Path = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)

    df["date"] = pd.to_datetime(df["date"])
    df["time"] = pd.to_datetime(df["time"], format="%H:%M").dt.time
    df["hour"] = pd.to_datetime(df["time"].astype(str)).dt.hour
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["week"] = df["date"].dt.isocalendar().week.astype(int)

    df["day_of_week"] = pd.Categorical(
        df["day_of_week"],
        categories=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        ordered=True,
    )

    df["total_price"] = df["quantity"] * df["unit_price"]

    assert df.isnull().sum().sum() == 0, "Unexpected nulls found in dataset"

    return df


if __name__ == "__main__":
    df = load_and_clean()
    print(f"Loaded {len(df)} rows, {df['date'].nunique()} unique days")
    print(df.dtypes)
