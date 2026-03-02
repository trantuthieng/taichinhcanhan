"""Savings repository."""

from typing import List
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.savings import SavingsDeposit, SavingsInterestEvent
from repositories.base import BaseRepository


class SavingsRepository(BaseRepository[SavingsDeposit]):
    def __init__(self, session: Session):
        super().__init__(SavingsDeposit, session)

    def get_by_user(self, user_id: int, status: str = None) -> List[SavingsDeposit]:
        q = self.session.query(SavingsDeposit).filter(
            SavingsDeposit.user_id == user_id,
            SavingsDeposit.is_deleted == 0,
        )
        if status:
            q = q.filter(SavingsDeposit.status == status)
        return q.order_by(SavingsDeposit.maturity_date).all()

    def get_active(self, user_id: int) -> List[SavingsDeposit]:
        return self.get_by_user(user_id, status="active")

    def get_maturing_soon(self, user_id: int, days: int = 30) -> List[SavingsDeposit]:
        from datetime import timedelta

        deadline = date.today() + timedelta(days=days)
        return (
            self.session.query(SavingsDeposit)
            .filter(
                SavingsDeposit.user_id == user_id,
                SavingsDeposit.status == "active",
                SavingsDeposit.is_deleted == 0,
                SavingsDeposit.maturity_date <= deadline,
            )
            .order_by(SavingsDeposit.maturity_date)
            .all()
        )

    def get_overdue(self, user_id: int) -> List[SavingsDeposit]:
        return (
            self.session.query(SavingsDeposit)
            .filter(
                SavingsDeposit.user_id == user_id,
                SavingsDeposit.status == "active",
                SavingsDeposit.is_deleted == 0,
                SavingsDeposit.maturity_date < date.today(),
            )
            .all()
        )

    def get_total_principal(self, user_id: int) -> float:
        result = (
            self.session.query(func.sum(SavingsDeposit.principal_amount))
            .filter(
                SavingsDeposit.user_id == user_id,
                SavingsDeposit.status == "active",
                SavingsDeposit.is_deleted == 0,
            )
            .scalar()
        )
        return result or 0.0


class SavingsInterestEventRepository(BaseRepository[SavingsInterestEvent]):
    def __init__(self, session: Session):
        super().__init__(SavingsInterestEvent, session)

    def get_by_savings(self, savings_id: int) -> List[SavingsInterestEvent]:
        return (
            self.session.query(SavingsInterestEvent)
            .filter(SavingsInterestEvent.savings_id == savings_id)
            .order_by(SavingsInterestEvent.event_date.desc())
            .all()
        )
