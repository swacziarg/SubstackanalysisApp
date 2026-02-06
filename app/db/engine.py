import os
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def get_engine() -> Engine:
    # Supabase gives you a Postgres connection string (DATABASE_URL)
    db_url = os.environ["DATABASE_URL"]
    return create_engine(db_url, pool_pre_ping=True)
