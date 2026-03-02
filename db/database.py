"""SQLAlchemy engine và session factory.

Thiết kế để dễ chuyển từ SQLite sang PostgreSQL:
chỉ cần đổi DATABASE_URL trong .env.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from config import settings

_connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    _connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=_connect_args,
    echo=False,
    pool_pre_ping=True,
)

# Bật WAL mode và foreign keys cho SQLite
if settings.DATABASE_URL.startswith("sqlite"):
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
