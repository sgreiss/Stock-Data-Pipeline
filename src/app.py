# app.py

import os
import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import get_engine
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Stock Dashboard", layout="wide")
st.title("Stock Data Dashboard")

engine = get_engine()

query = text("SELECT DISTINCT ticker FROM stock_data ORDER BY ticker")

with engine.connect() as conn:
    tickers = pd.read_sql(query, conn)["ticker"].tolist()

st.sidebar.header("Filter Options")
selected_tickers = st.sidebar.multiselect(
    "Select Ticker(s)", tickers, default=tickers[:1]
)
date_range = st.sidebar.date_input(
    "Select Date Range", [datetime(2020, 1, 1), datetime.today()]
)

if len(date_range) == 2 and selected_tickers:
    start_date, end_date = date_range

    query = text(
        """
        SELECT * FROM stock_data
        WHERE ticker = ANY(:tickers) 
        AND date BETWEEN :start_date AND :end_date
        ORDER BY ticker, date ASC
        """
    )

    params = {
        "tickers": selected_tickers,
        "start_date": start_date,
        "end_date": end_date,
    }

    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params=params)

else:
    df = pd.DataFrame()

if not df.empty:
    st.header("Metrics Overview")

    kpi_cols = st.columns(len(selected_tickers))

    for i, ticker in enumerate(selected_tickers):
        ticker_df = df[df["ticker"] == ticker]
        latest_close = ticker_df["close"].iloc[-1]
        pct_change = (
            (latest_close - ticker_df["close"].iloc[0]) / ticker_df["close"].iloc[0]
        ) * 100
        volatility = (
            ticker_df["vol20"].iloc[-1] if "vol20" in ticker_df.columns else None
        )

        with kpi_cols[i]:
            st.metric(f"{ticker} Latest Close", f"${latest_close:.2f}")
            st.metric(f"{ticker} YTD % Change", f"{pct_change:.2f}%")

            if volatility is not None:
                st.metric(f"{ticker} 20-Day Volatility", f"{volatility:.2f}")

    st.header("Stock Prices")

    for ticker in selected_tickers:
        ticker_df = df[df["ticker"] == ticker]

        st.markdown(f"### {ticker} Stock Price")

        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=ticker_df["date"],
                    open=ticker_df["open"],
                    high=ticker_df["high"],
                    low=ticker_df["low"],
                    close=ticker_df["close"],
                    name="Candlestick",
                )
            ]
        )

        fig.add_trace(
            go.Scatter(
                x=ticker_df["date"],
                y=ticker_df["close"],
                mode="lines",
                name="Close Price",
                line=dict(width=1.5),
            )
        )

        if "ma20" in ticker_df.columns:
            fig.add_trace(
                go.Scatter(
                    x=ticker_df["date"],
                    y=ticker_df["ma20"],
                    mode="lines",
                    name="20-Day MA",
                    line=dict(color="orange"),
                )
            )

        fig.update_layout(xaxis_rangeslider_visible=False, height=500)
        st.plotly_chart(fig, use_container_width=True)

    st.header("Daily Returns")

    for ticker in selected_tickers:
        ticker_df = df[df["ticker"] == ticker]
        fig = px.histogram(
            ticker_df,
            x="daily_return",
            nbins=50,
            title=f"{ticker} Daily Returns Distribution",
        )
        st.plotly_chart(fig, use_container_width=True)

    if len(selected_tickers) > 1:
        st.subheader("Correlation Heatmap")

        pivot_df = df.pivot(
            index="date", columns="ticker", values="daily_return"
        ).dropna()
        corr = pivot_df.corr()

        fig = px.imshow(
            corr,
            text_auto=True,
            title="Correlation Heatmap of Daily Returns",
        )
        st.plotly_chart(fig, use_container_width=True)
