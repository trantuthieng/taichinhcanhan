"""Goal service - Quản lý mục tiêu tài chính."""

import logging
from typing import List, Optional, Tuple
from datetime import date

from db.database import get_session
from models.goal import SavingsGoal
from repositories.goal_repo import GoalRepository
from repositories.audit_repo import AuditRepository

logger = logging.getLogger(__name__)


class GoalService:
    """Dịch vụ mục tiêu tiết kiệm."""

    @staticmethod
    def create_goal(user_id: int, name: str, target_amount: float,
                    current_amount: float = 0, target_date: date = None,
                    notes: str = None) -> Tuple[bool, str]:
        session = get_session()
        try:
            g = SavingsGoal(
                user_id=user_id,
                name=name,
                target_amount=target_amount,
                current_amount=current_amount,
                target_date=target_date,
                notes=notes,
                status="active",
            )
            session.add(g)
            AuditRepository(session).log_action(user_id, "create_goal", "goal", extra=name)
            session.commit()
            return True, "Tạo mục tiêu thành công"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi: {e}"
        finally:
            session.close()

    @staticmethod
    def update_goal(user_id: int, goal_id: int, **kwargs) -> Tuple[bool, str]:
        session = get_session()
        try:
            repo = GoalRepository(session)
            g = repo.get_by_id(goal_id)
            if not g or g.user_id != user_id:
                return False, "Không tìm thấy"
            for k, v in kwargs.items():
                if hasattr(g, k):
                    setattr(g, k, v)
            if g.current_amount >= g.target_amount and g.status == "active":
                g.status = "completed"
            session.commit()
            return True, "Cập nhật thành công"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi: {e}"
        finally:
            session.close()

    @staticmethod
    def contribute(user_id: int, goal_id: int, amount: float) -> Tuple[bool, str]:
        """Thêm tiền vào mục tiêu."""
        session = get_session()
        try:
            repo = GoalRepository(session)
            g = repo.get_by_id(goal_id)
            if not g or g.user_id != user_id:
                return False, "Không tìm thấy"
            if g.status != "active":
                return False, "Mục tiêu đã hoàn thành/hủy"
            g.current_amount += amount
            if g.current_amount >= g.target_amount:
                g.status = "completed"
            AuditRepository(session).log_action(user_id, "contribute_goal", "goal", extra=f"{amount}")
            session.commit()
            return True, "Đã thêm tiền vào mục tiêu"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi: {e}"
        finally:
            session.close()

    @staticmethod
    def get_goals(user_id: int, status: str = None) -> List[dict]:
        session = get_session()
        try:
            repo = GoalRepository(session)
            goals = repo.get_by_user(user_id, status)
            results = []
            for g in goals:
                pct = round(g.current_amount / g.target_amount * 100, 1) if g.target_amount > 0 else 0
                remaining = max(0, g.target_amount - g.current_amount)
                days_left = None
                if g.target_date:
                    days_left = (g.target_date - date.today()).days
                results.append({
                    "goal": g,
                    "percentage": pct,
                    "remaining": remaining,
                    "days_left": days_left,
                    "daily_needed": round(remaining / max(1, days_left), 0) if days_left and days_left > 0 else None,
                })
            return results
        finally:
            session.close()

    @staticmethod
    def cancel_goal(user_id: int, goal_id: int) -> Tuple[bool, str]:
        session = get_session()
        try:
            repo = GoalRepository(session)
            g = repo.get_by_id(goal_id)
            if not g or g.user_id != user_id:
                return False, "Không tìm thấy"
            g.status = "cancelled"
            session.commit()
            return True, "Đã hủy mục tiêu"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi: {e}"
        finally:
            session.close()
