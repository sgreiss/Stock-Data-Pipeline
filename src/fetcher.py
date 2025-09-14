# fetcher.py

import yfinance as yf
import pandas as pd
from typing import Optional


def fetch_yfinance(
    ticker: str,
    period: Optional[str] = "1y",
    interval: str = "1d",
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> pd.DataFrame:
    """
    Fetch historical market data from Yahoo Finance. Returns a pandas DataFrame.
    """

    # If start and end dates are provided, use them; otherwise, use period
    if start or end:
        data = yf.download(
            ticker,
            start=start,
            end=end,
            interval=interval,
            progress=False,
            auto_adjust=True,
        )
    else:
        data = yf.download(
            ticker, period=period, interval=interval, progress=False, auto_adjust=True
        )

    if data is None or data.empty:
        return pd.DataFrame()

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0] if col[1] == "" else col[0] for col in data.columns]

    data = data.reset_index()
    data["Ticker"] = ticker

    return data.rename(columns={"Date": "date"})


# fetch_alpha_vantage() ... could be implemented here
