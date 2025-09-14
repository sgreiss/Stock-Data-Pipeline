# test_fetcher.py

import pandas as pd
from src.fetcher import fetch_yfinance


def test_fetch_yfinance():
    """
    Test the fetch_yfinance function with a known ticker.
    """

    df = fetch_yfinance(ticker="AAPL", period="1mo", interval="1d")

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "Close" in df.columns
    assert "date" in df.columns

# Note: Testing fetch_alpha_vantage is omitted due to premium API key preference.