"""Transaction repository."""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from models.transaction import Transaction
from repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, session: Session):
        super().__init__(Transaction, session)

    def get_by_user(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        account_id: Optional[int] = None,
        category_id: Optional[int] = None,
        tx_type: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Transaction]:
        q = self.session.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.is_deleted == 0,
        )
        if start_date:
            q = q.filter(Transaction.transaction_date >= start_date)
        if end_date:
            q = q.filter(Transaction.transaction_date <= end_date)
        if account_id:
            q = q.filter(
                (Transaction.account_id == account_id) | (Transaction.to_account_id == account_id)
            )
        if category_id:
            q = q.filter(Transaction.category_id == category_id)
        if tx_type:
            q = q.filter(Transaction.type == tx_type)
        if search:
            q = q.filter(Transaction.description.ilike(f"%{search}%"))
        return q.order_by(Transaction.transaction_date.desc()).limit(limit).offset(offset).all()

    def count_by_user(self, user_id: int) -> int:
        return (
            self.session.query(func.count(Transaction.id))
            .filter(Transaction.user_id == user_id, Transaction.is_deleted == 0)
            .scalar()
            or 0
        )

    def sum_by_type_and_period(
        self, user_id: int, tx_type: str, start: datetime, end: datetime
    ) -> float:
        result = (
            self.session.query(func.sum(Transaction.amount))
            .filter(
                Transaction.user_id == user_id,
                Transaction.type == tx_type,
                Transaction.is_deleted == 0,
                Transaction.status == "completed",
                Transaction.transaction_date >= start,
                Transaction.transaction_date <= end,
            )
            .scalar()
        )
        return result or 0.0

    def get_by_category_period(
        self, user_id: int, tx_type: str, start: datetime, end: datetime
    ) -> List:
        from models.category import Category

        rows = (
            self.session.query(Category.name, Category.icon, func.sum(Transaction.amount))
            .join(Category, Transaction.category_id == Category.id)
            .filter(
                Transaction.user_id == user_id,
                Transaction.type == tx_type,
                Transaction.is_deleted == 0,
                Transaction.status == "completed",
                Transaction.transaction_date >= start,
                Transaction.transaction_date <= end,
            )
            .group_by(Category.name, Category.icon)
            .order_by(func.sum(Transaction.amount).desc())
            .all()
        )
        return rows

    def check_fingerprint(self, user_id: int, fingerprint: str) -> bool:
        return (
            self.session.query(Transaction)
            .filter(
                Transaction.user_id == user_id,
                Transaction.fingerprint == fingerprint,
                Transaction.is_deleted == 0,
            )
            .count()
            > 0
        )

    def get_monthly_trend(self, user_id: int, months: int = 12) -> List:
        """Xu hướng thu chi theo tháng."""
        from datetime import timedelta

        now = datetime.utcnow()
        start = datetime(now.year, now.month, 1) - timedelta(days=months * 31)
        rows = (
            self.session.query(
                func.strftime("%Y-%m", Transaction.transaction_date).label("month"),
                Transaction.type,
                func.sum(Transaction.amount),
            )
            .filter(
                Transaction.user_id == user_id,
                Transaction.is_deleted == 0,
                Transaction.status == "completed",
                Transaction.transaction_date >= start,
                Transaction.type.in_(["income", "expense"]),
            )
            .group_by("month", Transaction.type)
            .order_by("month")
            .all()
        )
        return rows
