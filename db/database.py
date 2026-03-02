"""SQLAlchemy engine và session factory.

Thiết kế để dễ chuyển từ SQLite sang PostgreSQL:
chỉ cần đổi DATABASE_URL trong .env.
"""

import logging

from sqlalchemy import create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session
from config import settings, DATA_DIR

logger = logging.getLogger(__name__)

database_url = settings.DATABASE_URL

# Supabase/Heroku style URL compatibility
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

def _build_engine(url: str):
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    elif url.startswith("postgresql"):
        url_obj = make_url(url)
        connect_args = {"connect_timeout": 10}
        if (url_obj.query or {}).get("sslmode") is None:
            connect_args["sslmode"] = "require"

    return create_engine(
        url,
        connect_args=connect_args,
        echo=False,
        pool_pre_ping=True,
    )


active_database_url = database_url
last_database_error: str = ""
engine = _build_engine(active_database_url)

# Nếu PostgreSQL lỗi (thường do DATABASE_URL/secret sai), fallback để app không crash
if active_database_url.startswith("postgresql"):
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql("SELECT 1")
    except Exception as exc:
        last_database_error = str(exc)
        fallback_url = f"sqlite:///{DATA_DIR / 'finance_fallback.db'}"
        logger.error(
            "Không kết nối được PostgreSQL/Supabase. Fallback sang SQLite. "
            "Kiểm tra DATABASE_URL trên Streamlit Secrets.",
            exc_info=exc,
        )
        active_database_url = fallback_url
        engine = _build_engine(active_database_url)


# Bật WAL mode và foreign keys cho SQLite
if active_database_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_session() -> Session:
    """Tạo database session mới."""
    session = SessionLocal()
    try:
        return session
    except Exception:
        session.close()
        raise


def get_active_database_url() -> str:
    """URL database đang hoạt động sau khi resolve fallback."""
    return active_database_url


def get_last_database_error() -> str:
    """Lỗi kết nối DB gần nhất (nếu có)."""
    return last_database_error
