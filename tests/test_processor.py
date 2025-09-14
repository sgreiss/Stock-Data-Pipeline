# test_processor.py

import pandas as pd
from src.processor import process_data


def test_process_data():
    """
    Test the process_data function with sample data.
    """

    data = {
        "date": pd.date_range(start="2023-01-01", periods=5, freq="D"),
        "Close": [150, 152, 151, 153, 155],
    }

    df = pd.DataFrame(data)
    processed_df = process_data(df)
    df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None)

    assert isinstance(processed_df, pd.DataFrame)
    assert "daily_return" in processed_df.columns
    assert "ma20" in processed_df.columns
    assert "vol20" in processed_df.columns
    assert pd.api.types.is_datetime64_any_dtype(processed_df["date"])
