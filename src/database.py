import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv("../.env")

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable is not set.")

engine = create_engine(DATABASE_URL)


def get_engine():
    return engine
