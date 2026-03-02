"""Goal repository."""

from typing import List
from sqlalchemy.orm import Session
from models.goal import SavingsGoal
from repositories.base import BaseRepository


class GoalRepository(BaseRepository[SavingsGoal]):
    def __init__(self, session: Session):
        super().__init__(SavingsGoal, session)

    def get_by_user(self, user_id: int, status: str = None) -> List[SavingsGoal]:
        q = self.session.query(SavingsGoal).filter(SavingsGoal.user_id == user_id)
        if status:
            q = q.filter(SavingsGoal.status == status)
        return q.order_by(SavingsGoal.priority.desc(), SavingsGoal.deadline).all()

    def get_active(self, user_id: int) -> List[SavingsGoal]:
        return self.get_by_user(user_id, status="active")
