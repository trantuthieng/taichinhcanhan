"""Budget service - Quản lý ngân sách."""

import logging
from typing import List, Optional, Tuple
from datetime import datetime

from db.database import get_session
from models.budget import Budget
from repositories.budget_repo import BudgetRepository
from repositories.audit_repo import AuditRepository
from services.transaction_service import TransactionService

logger = logging.getLogger(__name__)


class BudgetService:
    """Dịch vụ ngân sách."""

    @staticmethod
    def set_budget(user_id: int, category_id: Optional[int], amount: float, month: int, year: int, notes: str = None) -> Tuple[bool, str]:
        session = get_session()
        try:
            repo = BudgetRepository(session)
            existing = repo.get_by_category(user_id, category_id, month, year) if category_id else repo.get_overall(user_id, month, year)
            if existing:
                existing.amount = amount
                existing.notes = notes
            else:
                b = Budget(user_id=user_id, category_id=category_id, amount=amount, month=month, year=year, notes=notes)
                session.add(b)
            AuditRepository(session).log_action(user_id, "set_budget", "budget")
            session.commit()
            return True, "Cập nhật ngân sách thành công"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi: {e}"
        finally:
            session.close()

    @staticmethod
    def get_budgets(user_id: int, month: int, year: int) -> List[dict]:
        """Danh sách ngân sách kèm tiến độ chi tiêu."""
        session = get_session()
        try:
            repo = BudgetRepository(session)
            budgets = repo.get_by_user_period(user_id, month, year)

            start = datetime(year, month, 1)
            if month == 12:
                end = datetime(year + 1, 1, 1)
            else:
                end = datetime(year, month + 1, 1)

            results = []
            for b in budgets:
                # Tính chi tiêu thực tế cho category
                from repositories.transaction_repo import TransactionRepository
                tx_repo = TransactionRepository(session)

                if b.category_id:
                    spent = tx_repo.sum_by_type_and_period(user_id, "expense", start, end)
                    # Lọc theo category cụ thể
                    from sqlalchemy import func
                    from models.transaction import Transaction
                    cat_spent = (
                        session.query(func.sum(Transaction.amount))
                        .filter(
                            Transaction.user_id == user_id,
                            Transaction.type == "expense",
                            Transaction.category_id == b.category_id,
                            Transaction.is_deleted == 0,
                            Transaction.status == "completed",
                            Transaction.transaction_date >= start,
                            Transaction.transaction_date < end,
                        )
                        .scalar() or 0.0
                    )
                    spent = cat_spent
                else:
                    spent = tx_repo.sum_by_type_and_period(user_id, "expense", start, end)

                pct = round(spent / b.amount * 100, 1) if b.amount > 0 else 0
                results.append({
                    "budget": b,
                    "spent": spent,
                    "remaining": b.amount - spent,
                    "percentage": pct,
                    "is_over": spent > b.amount,
                })
            return results
        finally:
            session.close()

    @staticmethod
    def delete_budget(user_id: int, budget_id: int) -> Tuple[bool, str]:
        session = get_session()
        try:
            repo = BudgetRepository(session)
            b = repo.get_by_id(budget_id)
            if not b or b.user_id != user_id:
                return False, "Không tìm thấy"
            repo.delete(b)
            session.commit()
            return True, "Đã xóa ngân sách"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi: {e}"
        finally:
            session.close()
