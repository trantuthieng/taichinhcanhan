"""Budget repository."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.budget import Budget
from repositories.base import BaseRepository


class BudgetRepository(BaseRepository[Budget]):
    def __init__(self, session: Session):
        super().__init__(Budget, session)

    def get_by_user_period(self, user_id: int, month: int, year: int) -> List[Budget]:
        return (
            self.session.query(Budget)
            .filter(Budget.user_id == user_id, Budget.month == month, Budget.year == year)
            .all()
        )

    def get_by_category(self, user_id: int, category_id: int, month: int, year: int) -> Optional[Budget]:
        return (
            self.session.query(Budget)
            .filter(
                Budget.user_id == user_id,
                Budget.category_id == category_id,
                Budget.month == month,
                Budget.year == year,
            )
            .first()
        )

    def get_overall(self, user_id: int, month: int, year: int) -> Optional[Budget]:
        return (
            self.session.query(Budget)
            .filter(
                Budget.user_id == user_id,
                Budget.category_id == None,
                Budget.month == month,
                Budget.year == year,
            )
            .first()
        )
