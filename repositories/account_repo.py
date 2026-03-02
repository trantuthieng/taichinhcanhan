"""Account repository."""

from typing import List, Optional
from sqlalchemy.orm import Session
from models.account import Account
from repositories.base import BaseRepository


class AccountRepository(BaseRepository[Account]):
    def __init__(self, session: Session):
        super().__init__(Account, session)

    def get_by_user(self, user_id: int, include_inactive: bool = False) -> List[Account]:
        q = self.session.query(Account).filter(
            Account.user_id == user_id,
            Account.is_deleted == 0,
        )
        if not include_inactive:
            q = q.filter(Account.is_active == 1)
        return q.order_by(Account.sort_order, Account.name).all()

    def get_by_user_and_type(self, user_id: int, account_type: str) -> List[Account]:
        return (
            self.session.query(Account)
            .filter(
                Account.user_id == user_id,
                Account.account_type == account_type,
                Account.is_deleted == 0,
                Account.is_active == 1,
            )
            .all()
        )

    def get_total_balance_by_currency(self, user_id: int) -> dict:
        """Tổng số dư theo loại tiền."""
        from sqlalchemy import func

        rows = (
            self.session.query(Account.currency, func.sum(Account.balance))
            .filter(
                Account.user_id == user_id,
                Account.is_deleted == 0,
                Account.is_active == 1,
            )
            .group_by(Account.currency)
            .all()
        )
        return {r[0]: r[1] or 0.0 for r in rows}

    def update_balance(self, account_id: int, delta: float) -> None:
        acc = self.get_by_id(account_id)
        if acc:
            acc.balance = (acc.balance or 0.0) + delta
            self.session.flush()
