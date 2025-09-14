# storage.py

import os
import pandas as pd
from sqlalchemy import create_engine


def save_to_csv(df: pd.DataFrame, path: str) -> None:
    """
    Save DataFrame to a CSV file.
    """

    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)


def save_to_sqlite(
    df: pd.DataFrame, db_path: str, table_name: str = "stock_data"
) -> None:
    """
    Save DataFrame to a SQLite database.
    """

    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        df.to_sql(table_name, engine, if_exists="replace", index=False)
    finally:
        engine.dispose()
