"""Cấu hình chung cho ứng dụng quản lý tài chính cá nhân."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = DATA_DIR / "backups"

DATA_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)


class Settings:
    """Application settings loaded from environment."""

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'finance.db'}")

    # Admin defaults
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")
    ADMIN_DISPLAY_NAME: str = os.getenv("ADMIN_DISPLAY_NAME", "Quản trị viên")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default-secret-key-change-me")

    # VNAppMob API
    VNAPPMOB_BASE_URL: str = os.getenv("VNAPPMOB_BASE_URL", "https://api.vnappmob.com/api")
    VNAPPMOB_EXCHANGE_SCOPE: str = os.getenv("VNAPPMOB_EXCHANGE_SCOPE", "exchange_rate")
    VNAPPMOB_GOLD_SCOPE: str = os.getenv("VNAPPMOB_GOLD_SCOPE", "gold")

    # Vietcombank fallback
    VCB_EXCHANGE_URL: str = os.getenv(
        "VCB_EXCHANGE_URL",
        "https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx?b=10",
    )

    # Cache
    RATE_CACHE_TTL: int = int(os.getenv("RATE_CACHE_TTL", "1800"))
    GOLD_CACHE_TTL: int = int(os.getenv("GOLD_CACHE_TTL", "1800"))
    TOKEN_TTL: int = int(os.getenv("TOKEN_TTL", "3600"))

    # Backup
    AUTO_BACKUP_ON_START: bool = os.getenv("AUTO_BACKUP_ON_START", "true").lower() == "true"
    MAX_BACKUPS: int = int(os.getenv("MAX_BACKUPS", "10"))

    # App
    APP_NAME: str = "Quản Lý Tài Chính Cá Nhân"
    APP_VERSION: str = "1.0.0"
    DEFAULT_CURRENCY: str = "VND"


settings = Settings()
