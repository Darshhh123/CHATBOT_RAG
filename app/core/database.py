
import os
from functools import lru_cache

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Load environment variables from the root .env file
load_dotenv()


# Create one reusable database engine
@lru_cache
def get_engine():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is missing from .env")

    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return create_engine(
        database_url,
        pool_pre_ping=True,
        echo=False
    )


# Create database sessions for API requests
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine(), expire_on_commit=False)


# Dependency used by database-connected APIs
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Test Neon connection
def check_database_connection():
    with get_engine().connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return result.scalar()
