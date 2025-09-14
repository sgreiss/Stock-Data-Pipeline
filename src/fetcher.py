# fetcher.py

import requests
import yfinance as yf
import pandas as pd
from typing import Optional

from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="../keys/alpha_vantage.env")
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")


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

#development note: Alpha Vantage free tier does not support adjusted close prices
#development paused due to this reason
def fetch_alpha_vantage(ticker: str, output_size: str = "compact") -> pd.DataFrame:
    """
    Fetch historical market data from Alpha Vantage. Returns a pandas DataFrame.
    """

    if ALPHA_VANTAGE_KEY is None:
        raise ValueError("Alpha Vantage API key not found in environment variables.")

    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": ticker,
        "outputsize": output_size,
        "apikey": ALPHA_VANTAGE_KEY,
        "datatype": "json",
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    print(data)

    if "Error Message" in data:
        raise ValueError(f"Error fetching data for {ticker}: {data['Error Message']}")
    if "Time Series (Daily)" not in data:
        raise ValueError(f"No daily time series data found for {ticker}.")

    time_series = data.get("Time Series (Daily)") or {}
    rows = []

    for date, vals in time_series.items():
        try:
            rows.append(
                {
                    "date": pd.to_datetime(date),
                    "Open": float(vals["1. open"]),
                    "High": float(vals["2. high"]),
                    "Low": float(vals["3. low"]),
                    "Close": float(vals["4. close"]),
                    "Adj Close": float(vals.get("5. adjusted close", vals["4. close"])),
                    "Volume": int(vals["6. volume"], 0),
                    "Ticker": ticker,
                }
            )
        except (KeyError, ValueError) as e:
            print(f"Skipping date {date} due to error: {e}")
            continue

    if not rows:
        raise ValueError(f"No valid data rows found for {ticker}.")

    df = pd.DataFrame(rows)

    if "date" in df.columns:
        df = df.sort_values("date").reset_index(drop=True)
    else:
        raise ValueError("Date column missing in fetched data.")

    return df
