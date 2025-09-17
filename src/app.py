# app.py

import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import get_engine
from datetime import datetime

st.set_page_config(page_title="Stock Dashboard", layout="wide")
st.title("Stock Data Dashboard")

engine = get_engine()

query = text("SELECT DISTINCT ticker FROM stock_data")
tickers = pd.read_sql(query, engine)["ticker"].tolist()
selected_tickers = st.multiselect("Select Ticker(s)", tickers, default=tickers[:1])

min_date = datetime(2000, 1, 1)
max_date = datetime.today()
start_date = st.date_input("Start Date", min_date)
end_date = st.date_input("End Date", max_date)

for ticker in selected_tickers:
    query = text(
        """
        SELECT * FROM stock_data
        WHERE ticker = :ticker AND date BETWEEN :start_date AND :end_date
        ORDER BY date ASC
        """
    )

    df = pd.read_sql(
        query,
        engine,
        params={"ticker": ticker, "start_date": start_date, "end_date": end_date},
    )

    if df.empty:
        st.warning(f"No data available for {ticker} in the selected date range.")
        continue

    st.subheader(f"{ticker} Stock Price")
    st.line_chart(df.set_index("date")[["close", "ma20"]])

    st.subheader(f"{ticker} Daily Returns & Volatility")
    st.line_chart(df.set_index("date")[["daily_return", "vol20"]])
