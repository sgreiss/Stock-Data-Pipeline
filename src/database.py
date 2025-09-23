import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv("../.env")

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable is not set.")

engine = create_engine(DATABASE_URL)


def get_engine():
    return engine


def fetch_stock_data(_query, _engine, params):
    with _engine.connect() as conn:
        return pd.read_sql(_query, conn, params=params)
