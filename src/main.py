# main.py

import argparse
import os
import logging
from text_colors import Colors as c
from fetcher import fetch_yfinance
from processor import process_data
from storage import save_to_csv, save_to_sqlite

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def run(tickers, period, interval, csv_dir, sqlite_db) -> None:
    logging.info(f"{c.GREEN}Starting data pipeline...{c.END}\n")

    for ticker in tickers:
        logging.info(
            f"{c.GREEN}Fetching data for {c.PURPLE}{ticker}{c.GREEN} with period={c.PURPLE}{period}{c.GREEN} and interval={c.PURPLE}{interval}{c.GREEN}...{c.END}\n"
        )
        data = fetch_yfinance(ticker=ticker, period=period, interval=interval)

        if data.empty:
            logging.warning(
                f"{c.RED}No data fetched for {c.PURPLE}{ticker}{c.RED}.{c.END}\n"
            )
            continue

        logging.info(
            f"{c.GREEN}Processing data for {c.PURPLE}{ticker}{c.GREEN}...{c.END}\n"
        )
        processed_data = process_data(data)

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
    run(tickers, args.period, args.interval, args.csv_dir, args.sqlite_db)

# example usage: python main.py --tickers AAPL,MSFT --period 6mo --interval 1dF
# run venv with .venv\Scripts\activate
