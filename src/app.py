# app.py

import streamlit as st
import pandas as pd
import os
from datetime import datetime

CSV_DIR = "../data/csv"

st.set_page_config(page_title="Stock Dashboard", layout="wide")
st.title("Stock Data Dashboard")

tickers = [f.split(".csv")[0] for f in os.listdir(CSV_DIR) if f.endswith(".csv")]
selected_ticker = st.multiselect("Select Ticker(s)", tickers, default=tickers[:1])

min_date = datetime(2000, 1, 1)
max_date = datetime.today()
start_date = st.date_input("Start Date", min_date)
end_date = st.date_input("End Date", max_date)

for ticker in selected_ticker:
    file_path = os.path.join(CSV_DIR, f"{ticker}.csv")
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, parse_dates=["date"])
        df["date"] = df["date"].dt.tz_convert(None)
        mask = (df["date"] >= pd.to_datetime(start_date)) & (
            df["date"] <= pd.to_datetime(end_date)
        )
        df = df.loc[mask]

        st.subheader(f"{ticker} Stock Price")
        st.line_chart(df.set_index("date")[["Close", "ma20"]])

        st.subheader(f"{ticker} Daily Returns & Volatility")
        st.line_chart(df.set_index("date")[["daily_return", "vol20"]])
    else:
        st.warning(f"No data found for ticker: {ticker}")
        continue
