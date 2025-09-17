# processor.py

import pandas as pd


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean data; set timezone to UTC; computer daily return, moving average, and volatility.
    Returns a new DataFrame with processed data.
    """

    if df is None or df.empty:
        return df

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])

    if (
        pd.api.types.is_datetime64_any_dtype(df["date"])
        and df["date"].dt.tz is not None
    ):
        df["date"] = df["date"].dt.tz_convert(None)

    # Ensure timezone is UTC
    if df["date"].dt.tz is None:
        df["date"] = df["date"].dt.tz_localize("UTC")
    else:
        df["date"] = df["date"].dt.tz_convert("UTC")

    df = df.sort_values("date").reset_index(drop=True)

    if "close" not in df.columns:
        raise ValueError(
            "DataFrame must contain 'close' column to compute daily returns."
        )

    # Calculate daily return, 20-day moving average, and 20-day volatility
    df["daily_return"] = df["close"].pct_change()
    df["ma20"] = df["close"].rolling(window=20, min_periods=1).mean()
    df["vol20"] = df["daily_return"].rolling(window=20, min_periods=1).std()

    df = df.dropna(subset=["close"]).reset_index(drop=True)

    return df
