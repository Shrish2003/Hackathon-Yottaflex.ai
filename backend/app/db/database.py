"""
SQLAlchemy engine and session management.
Provides get_db dependency and actual PostgreSQL connectivity check.
"""

import re
from typing import Generator, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy 2.x declarative models."""
    pass


# Create SQLAlchemy engine with pool_pre_ping for resilient connections and 3s timeout
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args={"connect_timeout": 3},
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator:
    """Dependency for providing database sessions per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def sanitize_error(error_message: str) -> str:
    """Sanitize error messages to ensure no passwords or credentials leak into logs or responses."""
    # Mask user:password in URIs
    sanitized = re.sub(r"://([^:@]+):([^@]+)@", r"://\1:***@", error_message)
    # Mask password parameters
    sanitized = re.sub(r"password=['\"][^'\"]*['\"]", "password='***'", sanitized, flags=re.IGNORECASE)
    return sanitized


def check_db_connection() -> Dict[str, Any]:
    """
    Executes a real SELECT 1 query against PostgreSQL.
    Reports actual connection status, database name, and sanitized error if disconnected.
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            if result == 1:
                db_name = engine.url.database or "unknown"
                return {
                    "connected": True,
                    "status": "connected",
                    "database": db_name,
                    "message": "PostgreSQL connection verified successfully via SELECT 1 query.",
                }
            return {
                "connected": False,
                "status": "unhealthy",
                "database": engine.url.database or "unknown",
                "message": "Query executed but returned unexpected result.",
            }
    except Exception as exc:
        sanitized_msg = sanitize_error(str(exc))
        return {
            "connected": False,
            "status": "disconnected",
            "database": engine.url.database or "unknown",
            "error": sanitized_msg,
            "message": "Failed to connect to PostgreSQL server.",
        }
