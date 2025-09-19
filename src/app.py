# app.py

import os
import streamlit as st
import pandas as pd
from sqlalchemy import text, inspect
from database import get_engine, fetch_stock_data
from main import run
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Stock Dashboard", layout="wide")
st.title("Stock Data Dashboard")

engine = get_engine()
inspector = inspect(engine)

if "stock_data" not in inspector.get_table_names():
    tickers = []
else:
    query = text("SELECT DISTINCT ticker FROM stock_data ORDER BY ticker")

    tickers = fetch_stock_data(query, engine, None)["ticker"].tolist()


# sidebar
st.sidebar.header("Filter Options")
selected_tickers = st.sidebar.multiselect("Select Ticker(s)", tickers, default=tickers)
date_range = st.sidebar.date_input(
    "Select Date Range", [datetime(2020, 1, 1), datetime.today()]
)

st.sidebar.header("Display Options")
show_metrics = st.sidebar.checkbox("Show Metrics", value=True)
show_ind_closing_graph = st.sidebar.checkbox(
    "Show Individual Closing Price Graphs", value=True
)
show_all_closing_graph = st.sidebar.checkbox(
    "Show All Closing Prices on One Graph", value=False
)
show_daily_returns = st.sidebar.checkbox("Show Daily Returns", value=True)
show_correlation_heatmap = st.sidebar.checkbox("Show Correlation Heatmap", value=True)

st.sidebar.header("Data Manager")

with st.sidebar.expander("Load New Data"):
    tickers_input = st.text_input("Enter Tickers (comma separated)", value="AAPL,MSFT")
    source = st.selectbox("Data Source", ["yfinance", "alpha_vantage"], index=0)

    period = st.selectbox(
        "Data Period",
        ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "ytd", "max"],
        index=4,
    )
    interval = st.selectbox(
        "Data Interval",
        ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1d", "5d", "1wk", "1mo", "3mo"],
        index=7,
    )

    if st.button("Run Data Pipeline"):
        tickers_list = [ticker.strip().upper() for ticker in tickers_input.split(",")]
        st.info("Running data pipeline... This may take a few moments.")

        try:
            run(
                tickers_list,
                source,
                period,
                interval,
                csv_dir=None,
                sqlite_db=None,
            )
            st.success("Data pipeline executed. Refreshsing...")
            st.rerun()
        except Exception as e:
            st.error(f"Error running data pipeline: {e}")

    with st.sidebar.expander("Clear Data"):
        confirm = st.checkbox("Are you sure you want to delete all data?", value=False)
        if st.button("Clear All Data"):
            if confirm:
                with engine.connect() as conn:
                    conn.execute(text("DELETE FROM stock_data"))
                    conn.commit()
                st.success("All data cleared from the database.")
                st.rerun()
            else:
                st.warning("Please confirm to delete all data.")

# retrieve data
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

    df = fetch_stock_data(query, engine, params=params)

else:
    df = pd.DataFrame()


# content
if not df.empty:
    if show_metrics:
        st.divider()
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

    if show_ind_closing_graph:
        st.divider()
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

            fig.update_layout(xaxis_rangeslider_visible=False, height=500, xaxis_title="Date", yaxis_title="Price (USD)")
            st.plotly_chart(fig, use_container_width=True)

    if show_all_closing_graph and len(selected_tickers) > 1:
        st.divider()
        st.header("All Selected Stocks Closing Prices")

        fig = go.Figure()

        for ticker in selected_tickers:
            ticker_df = df[df["ticker"] == ticker]
            fig.add_trace(
                go.Scatter(
                    x=ticker_df["date"],
                    y=ticker_df["close"],
                    mode="lines",
                    name=ticker,
                )
            )

        fig.update_layout(xaxis_rangeslider_visible=False, height=600, xaxis_title="Date", yaxis_title="Price (USD)")
        st.plotly_chart(fig, use_container_width=True)

    if show_daily_returns:
        st.divider()
        st.header("Daily Returns")

        for ticker in selected_tickers:
            ticker_df = df[df["ticker"] == ticker]
            fig = px.histogram(
                ticker_df,
                x="daily_return",
                nbins=50,
                title=f"{ticker} Daily Returns Distribution",
                labels={"daily_return": "Daily Return", "count": "Frequency"},
            )
            st.plotly_chart(fig, use_container_width=True)

    if show_correlation_heatmap and len(selected_tickers) > 1:
        st.divider()
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

    if not (
        show_metrics
        or show_ind_closing_graph
        or show_daily_returns
        or show_correlation_heatmap
    ):
        st.info("Select at least one display option from the sidebar to view data.")

else:
    st.warning(
        "No data available for the selected filters. Please adjust your filters or load new data."
    )
