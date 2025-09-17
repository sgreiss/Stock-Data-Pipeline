# main.py

import argparse
import os
import logging
from text_colors import Colors as c
from fetcher import fetch_yfinance, fetch_alpha_vantage
from processor import process_data
from storage import save_to_csv, save_to_sqlite
from database import get_engine

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def run(tickers, source, period, interval, csv_dir, sqlite_db) -> None:
    logging.info(f"{c.GREEN}Starting data pipeline...{c.END}\n")

    for ticker in tickers:
        logging.info(
            f"{c.GREEN}Fetching data for {c.PURPLE}{ticker}{c.GREEN} with period={c.PURPLE}{period}{c.GREEN} and interval={c.PURPLE}{interval}{c.GREEN} from {c.PURPLE}{source}{c.GREEN}...{c.END}\n"
        )

        if source == "yfinance":
            data = fetch_yfinance(ticker=ticker, period=period, interval=interval)
        elif source == "alpha_vantage":
            data = fetch_alpha_vantage(ticker=ticker)
        else:
            logging.error(
                f"{c.RED}Unknown data source: {c.PURPLE}{source}{c.RED}.{c.END}\n"
            )
            continue

        if data.empty:
            logging.warning(
                f"{c.RED}No data fetched for {c.PURPLE}{ticker}{c.RED}.{c.END}\n"
            )
            continue

        logging.info(
            f"{c.GREEN}Processing data for {c.PURPLE}{ticker}{c.GREEN}...{c.END}\n"
        )
        processed_data = process_data(data)

        engine = get_engine()
        processed_data.to_sql(
            name="stock_data", con=engine, if_exists="append", index=False
        )

        processed_data["Ticker"] = ticker

        csv_path = os.path.join(csv_dir, f"{ticker}.csv")
        logging.info(
            f"{c.GREEN}Saving data for {c.PURPLE}{ticker}{c.GREEN} to CSV with path {c.PURPLE}{csv_path}{c.GREEN}...{c.END}\n"
        )
        save_to_csv(df=processed_data, path=csv_path)

        logging.info(
            f"{c.GREEN}Saving data for {c.PURPLE}{ticker}{c.GREEN} to SQLite database {c.PURPLE}{sqlite_db}{c.GREEN}...{c.END}\n"
        )
        save_to_sqlite(df=processed_data, db_path=sqlite_db, table_name="stock_data")

    logging.info(f"{c.BLUE}Data pipeline completed.{c.END}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stock Data Pipeline")
    parser.add_argument(
        "--tickers", type=str, default="AAPL", help="Comma separated tickers"
    )
    parser.add_argument(
        "--source",
        type=str,
        default="yfinance",
        choices=["yfinance", "alpha_vantage"],
        help="Data source",
    )
    parser.add_argument("--period", type=str, default="1y", help="Data period")
    parser.add_argument("--interval", type=str, default="1d", help="Data interval")
    parser.add_argument(
        "--csv_dir", type=str, default="../data/csv", help="Directory to save CSV files"
    )
    parser.add_argument(
        "--sqlite_db",
        type=str,
        default="../data/stock_data.db",
        help="SQLite database path",
    )
    args = parser.parse_args()

    tickers = [ticker.strip().upper() for ticker in args.tickers.split(",")]
    run(tickers, args.source, args.period, args.interval, args.csv_dir, args.sqlite_db)

# example usage: python main.py --tickers AAPL,MSFT --source yfinance --period 6mo --interval 1d
# run venv with .venv\Scripts\activate
