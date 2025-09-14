# test_storage.py

import os
import pandas as pd
import tempfile
from src.storage import save_to_csv, save_to_sqlite
from sqlalchemy import create_engine


def make_sample_data():
    """
    Create a sample DataFrame for testing.
    """

    data = {
        "date": pd.date_range(start="2023-01-01", periods=3, freq="D"),
        "Close": [100, 102, 101],
        "daily_return": [0.0, 0.0133, -0.0066],
        "ma20": [100, 100.5, 101],
        "vol20": [0, 0.005, 0.004],
    }
    return pd.DataFrame(data)


def test_save_to_csv():
    """
    Test saving DataFrame to CSV.
    """

    df = make_sample_data()
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, "test.csv")
        save_to_csv(df, csv_path)
        assert os.path.exists(csv_path)
        loaded_df = pd.read_csv(csv_path, parse_dates=["date"])
        pd.testing.assert_frame_equal(df.reset_index(drop=True), loaded_df)


def test_save_to_sqlite():
    """
    Test saving DataFrame to SQLite database.
    """

    df = make_sample_data()
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        save_to_sqlite(df, db_path, "test_table")

        engine = create_engine(f"sqlite:///{db_path}")
        try:
            with engine.connect() as conn:
                result = pd.read_sql("SELECT * FROM test_table", conn, parse_dates=["date"])
        finally:
            engine.dispose()

        assert not result.empty
        pd.testing.assert_frame_equal(df.reset_index(drop=True), result)

