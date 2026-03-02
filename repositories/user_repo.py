"""User repository."""

from typing import Optional
from sqlalchemy.orm import Session
from models.user import User
from repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: Session):
        super().__init__(User, session)

    def get_by_username(self, username: str) -> Optional[User]:
        return self.session.query(User).filter(User.username == username).first()

    def get_active_users(self):
        return self.session.query(User).filter(User.is_active == 1).all()

    def username_exists(self, username: str) -> bool:
        return self.session.query(User).filter(User.username == username).count() > 0
