"""SQLAlchemy engine và session factory.

Thiết kế để dễ chuyển từ SQLite sang PostgreSQL:
chỉ cần đổi DATABASE_URL trong .env.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker, Session
from config import settings

database_url = settings.DATABASE_URL

# Supabase/Heroku style URL compatibility
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

_connect_args = {}
if database_url.startswith("sqlite"):
    _connect_args = {"check_same_thread": False}
elif database_url.startswith("postgresql"):
    url_obj = make_url(database_url)
    if (url_obj.query or {}).get("sslmode") is None:
        _connect_args = {"sslmode": "require"}

engine = create_engine(
    database_url,
    connect_args=_connect_args,
    echo=False,
    pool_pre_ping=True,
)

# Bật WAL mode và foreign keys cho SQLite
if database_url.startswith("sqlite"):
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
