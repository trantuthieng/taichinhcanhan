"""Base repository - CRUD chung."""

from typing import TypeVar, Generic, Type, Optional, List
from sqlalchemy.orm import Session
from models.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Generic repository cho CRUD cơ bản."""

    def __init__(self, model: Type[T], session: Session):
        self.model = model
        self.session = session

    def get_by_id(self, id: int) -> Optional[T]:
        return self.session.query(self.model).filter(self.model.id == id).first()

    def get_all(self) -> List[T]:
        return self.session.query(self.model).all()

    def create(self, obj: T) -> T:
        self.session.add(obj)
        self.session.flush()
        return obj

    def update(self, obj: T, data: dict) -> T:
        for key, value in data.items():
            if value is not None and hasattr(obj, key):
                setattr(obj, key, value)
        self.session.flush()
        return obj

    def delete(self, obj: T) -> None:
        self.session.delete(obj)
        self.session.flush()

    def soft_delete(self, obj: T) -> T:
        if hasattr(obj, "is_deleted"):
            obj.is_deleted = 1
            self.session.flush()
        return obj

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
