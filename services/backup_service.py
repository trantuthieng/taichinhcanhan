"""Backup service - Sao lưu & khôi phục SQLite."""

import logging
import os
import shutil
from datetime import datetime
from typing import List, Tuple

from config import settings

logger = logging.getLogger(__name__)


class BackupService:
    """Sao lưu / khôi phục database SQLite."""

    BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backups")

    @classmethod
    def _ensure_dir(cls):
        os.makedirs(cls.BACKUP_DIR, exist_ok=True)

    @classmethod
    def _db_path(cls) -> str:
        url = settings.DATABASE_URL
        if url.startswith("sqlite:///"):
            return url.replace("sqlite:///", "")
        return "finance.db"

    @classmethod
    def create_backup(cls, label: str = "") -> Tuple[bool, str]:
        cls._ensure_dir()
        db = cls._db_path()
        if not os.path.exists(db):
            return False, "Không tìm thấy database"
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        bak_name = f"backup_{ts}_{label}.db" if label else f"backup_{ts}.db"
        dest = os.path.join(cls.BACKUP_DIR, bak_name)
        try:
            # Dùng SQLite backup API qua connection
            import sqlite3
            src_conn = sqlite3.connect(db)
            dst_conn = sqlite3.connect(dest)
            src_conn.backup(dst_conn)
            dst_conn.close()
            src_conn.close()
            logger.info("Backup created: %s", dest)
            cls._cleanup_old()
            return True, dest
        except Exception as e:
            logger.error("Backup failed: %s", e)
            return False, f"Lỗi: {e}"

    @classmethod
    def restore_backup(cls, backup_path: str) -> Tuple[bool, str]:
        if not os.path.exists(backup_path):
            return False, "File backup không tồn tại"
        db = cls._db_path()
        try:
            # Đóng tất cả connections trước
            from db.database import engine
            engine.dispose()

            # Copy đè
            import sqlite3
            src_conn = sqlite3.connect(backup_path)
            dst_conn = sqlite3.connect(db)
            src_conn.backup(dst_conn)
            dst_conn.close()
            src_conn.close()
            logger.info("Restore completed from: %s", backup_path)
            return True, "Khôi phục thành công. Vui lòng tải lại ứng dụng."
        except Exception as e:
            logger.error("Restore failed: %s", e)
            return False, f"Lỗi: {e}"

    @classmethod
    def list_backups(cls) -> List[dict]:
        cls._ensure_dir()
        files = []
        for f in os.listdir(cls.BACKUP_DIR):
            if f.endswith(".db"):
                path = os.path.join(cls.BACKUP_DIR, f)
                size = os.path.getsize(path)
                mtime = datetime.fromtimestamp(os.path.getmtime(path))
                files.append({"name": f, "path": path, "size_mb": round(size / 1024 / 1024, 2), "date": mtime})
        files.sort(key=lambda x: x["date"], reverse=True)
        return files

    @classmethod
    def _cleanup_old(cls):
        """Giữ tối đa n bản backup."""
        max_keep = getattr(settings, "BACKUP_MAX_COUNT", 10)
        backups = cls.list_backups()
        if len(backups) > max_keep:
            for old in backups[max_keep:]:
                try:
                    os.remove(old["path"])
                    logger.info("Removed old backup: %s", old["name"])
                except OSError:
                    pass

    @classmethod
    def export_db(cls) -> str:
        """Trả path tới file DB hiện tại cho download."""
        return cls._db_path()
