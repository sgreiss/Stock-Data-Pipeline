# fetcher.py

import yfinance as yf
import pandas as pd
import requests
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

    if start or end:
        data = yf.download(
            ticker, start=start, end=end, interval=interval, progress=False
        )
    else:
        data = yf.download(ticker, period=period, interval=interval, progress=False)

    if data is None or data.empty:
        return pd.DataFrame()

    data = data.reset_index().rename(columns={"Date": "date"})

    cols = [
        c
        for c in ["date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]
        if c in data.columns
    ]

    return data[cols]
