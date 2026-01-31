"""
Database configuration and session management.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Database URL - defaults to SQLite for development, PostgreSQL-ready
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./hr_portal.db"
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # Set to True for SQL logging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency for getting database sessions.
    
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
