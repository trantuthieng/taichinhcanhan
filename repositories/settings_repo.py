"""Settings repository."""

from typing import Optional
from sqlalchemy.orm import Session
from models.settings import UserSetting
from repositories.base import BaseRepository


class SettingsRepository(BaseRepository[UserSetting]):
    def __init__(self, session: Session):
        super().__init__(UserSetting, session)

    def get_value(self, user_id: int, key: str) -> Optional[str]:
        s = (
            self.session.query(UserSetting)
            .filter(UserSetting.user_id == user_id, UserSetting.key == key)
            .first()
        )
        return s.value if s else None

    def set_value(self, user_id: int, key: str, value: str) -> UserSetting:
        s = (
            self.session.query(UserSetting)
            .filter(UserSetting.user_id == user_id, UserSetting.key == key)
            .first()
        )
        if s:
            s.value = value
        else:
            s = UserSetting(user_id=user_id, key=key, value=value)
            self.session.add(s)
        self.session.flush()
        return s

    def get_all_for_user(self, user_id: int) -> dict:
        rows = self.session.query(UserSetting).filter(UserSetting.user_id == user_id).all()
        return {r.key: r.value for r in rows}
