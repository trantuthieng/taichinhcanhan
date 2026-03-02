"""Settings service - Cài đặt người dùng."""

import logging
from typing import Optional, Dict

from db.database import get_session
from repositories.settings_repo import SettingsRepository
from repositories.audit_repo import AuditRepository

logger = logging.getLogger(__name__)


class SettingsService:
    """Dịch vụ cài đặt."""

    DEFAULTS = {
        "currency": "VND",
        "language": "vi",
        "theme": "light",
        "date_format": "dd/mm/yyyy",
        "page_size": "20",
        "auto_backup": "true",
        "fx_auto_sync": "true",
        "gold_auto_sync": "true",
    }

    @staticmethod
    def get_setting(user_id: int, key: str) -> str:
        session = get_session()
        try:
            repo = SettingsRepository(session)
            val = repo.get_value(user_id, key)
            return val if val is not None else SettingsService.DEFAULTS.get(key, "")
        finally:
            session.close()

    @staticmethod
    def set_setting(user_id: int, key: str, value: str) -> bool:
        session = get_session()
        try:
            repo = SettingsRepository(session)
            repo.set_value(user_id, key, value)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error("Set setting error: %s", e)
            return False
        finally:
            session.close()

    @staticmethod
    def get_all_settings(user_id: int) -> Dict[str, str]:
        session = get_session()
        try:
            repo = SettingsRepository(session)
            stored = repo.get_all(user_id)
            result = dict(SettingsService.DEFAULTS)
            for s in stored:
                result[s.key] = s.value
            return result
        finally:
            session.close()

    @staticmethod
    def bulk_update(user_id: int, settings_dict: Dict[str, str]) -> bool:
        session = get_session()
        try:
            repo = SettingsRepository(session)
            for k, v in settings_dict.items():
                repo.set_value(user_id, k, str(v))
            AuditRepository(session).log_action(user_id, "update_settings", "settings")
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error("Bulk update settings error: %s", e)
            return False
        finally:
            session.close()
