"""
connection.py
--------------
This file sets up the connection to our SQLite database using SQLAlchemy.

Key concepts for viva:
- `engine`      -> the actual connection to the SQLite file (health_assistant.db)
- `SessionLocal`-> a factory that creates a new database "session" (a working
                    conversation with the DB) for every request
- `Base`        -> the base class that all our ORM models (tables) inherit from
- `get_db()`    -> a FastAPI "dependency" that opens a session, gives it to the
                    route function, and closes it automatically afterwards
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load variables from the .env file (e.g. DATABASE_URL, SECRET_KEY, AI API KEY)
load_dotenv()

# Default to a local SQLite file if no DATABASE_URL is provided in .env
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./health_assistant.db")

# `check_same_thread` is required only for SQLite when used with FastAPI,
# because FastAPI can use multiple threads to handle requests.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Every instance of SessionLocal will be a new database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All ORM models (tables) will inherit from this Base class
Base = declarative_base()


def get_db():
    """
    FastAPI dependency function.

    Usage in a route:
        def my_route(db: Session = Depends(get_db)):
            ...

    It opens one database session per request and guarantees it is closed
    afterwards, even if an error occurs (thanks to try/finally).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
