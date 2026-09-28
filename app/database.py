import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


load_dotenv()


# ---------------------------------------------------------
# Database Environment Variables
# ---------------------------------------------------------

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


# ---------------------------------------------------------
# Validate Required Database Configuration
# ---------------------------------------------------------

required_db_vars = {
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASSWORD,
    "DB_HOST": DB_HOST,
    "DB_PORT": DB_PORT,
    "DB_NAME": DB_NAME,
}

missing_vars = [
    key for key, value in required_db_vars.items()
    if not value
]

if missing_vars:
    raise RuntimeError(
        f"Missing required database environment variables: "
        f"{', '.join(missing_vars)}"
    )


# ---------------------------------------------------------
# Database URL
# ---------------------------------------------------------

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
)


# ---------------------------------------------------------
# Database Engine
# ---------------------------------------------------------

engine = create_engine(
    DATABASE_URL,

    # Detect stale database connections automatically
    pool_pre_ping=True,

    # Connection pool configuration
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
)


# ---------------------------------------------------------
# Database Session
# ---------------------------------------------------------

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# ---------------------------------------------------------
# SQLAlchemy Base
# ---------------------------------------------------------

class Base(DeclarativeBase):
    pass
