"""Transaction service - Quản lý giao dịch thu chi."""

import logging
import hashlib
from typing import List, Optional, Tuple
from datetime import datetime

from db.database import get_session
from models.transaction import Transaction
from repositories.transaction_repo import TransactionRepository
from repositories.account_repo import AccountRepository
from repositories.audit_repo import AuditRepository
from schemas.transaction import TransactionCreate, TransactionUpdate

logger = logging.getLogger(__name__)


def _make_fingerprint(user_id: int, data: TransactionCreate) -> str:
    """Tạo fingerprint chống nhập trùng."""
    raw = f"{user_id}|{data.account_id}|{data.amount}|{data.type}|{data.transaction_date.strftime('%Y-%m-%d')}|{data.category_id}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


class TransactionService:
    """Dịch vụ giao dịch."""

    @staticmethod
    def create_transaction(user_id: int, data: TransactionCreate) -> Tuple[bool, str, Optional[int]]:
        session = get_session()
        try:
            tx_repo = TransactionRepository(session)
            acc_repo = AccountRepository(session)

            # Kiểm tra fingerprint chống trùng
            fp = _make_fingerprint(user_id, data)
            if tx_repo.check_fingerprint(user_id, fp):
                return False, "Giao dịch tương tự đã tồn tại (có thể bị trùng)", None

            # Tạo giao dịch
            tx = Transaction(
                user_id=user_id,
                account_id=data.account_id,
                to_account_id=data.to_account_id,
                category_id=data.category_id,
                subcategory_id=data.subcategory_id,
                type=data.type,
                amount=data.amount,
                currency=data.currency,
                description=data.description,
                tags=data.tags,
                notes=data.notes,
                status="completed",
                fingerprint=fp,
                transaction_date=data.transaction_date,
            )
            tx_repo.create(tx)

            # Cập nhật số dư tài khoản
            if data.type == "income":
                acc_repo.update_balance(data.account_id, data.amount)
            elif data.type == "expense":
                acc_repo.update_balance(data.account_id, -data.amount)
            elif data.type == "transfer":
                acc_repo.update_balance(data.account_id, -data.amount)
                if data.to_account_id:
                    acc_repo.update_balance(data.to_account_id, data.amount)
            elif data.type == "adjustment":
                # Điều chỉnh trực tiếp - amount là delta
                acc_repo.update_balance(data.account_id, data.amount)

            AuditRepository(session).log_action(
                user_id, "create_transaction", "transaction", tx.id
            )
            session.commit()
            return True, "Giao dịch đã được ghi nhận", tx.id

        except Exception as e:
            session.rollback()
            logger.error(f"Lỗi tạo giao dịch: {e}")
            return False, f"Lỗi: {e}", None
        finally:
            session.close()

    @staticmethod
    def get_transactions(
        user_id: int,
        start_date: datetime = None,
        end_date: datetime = None,
        account_id: int = None,
        category_id: int = None,
        tx_type: str = None,
        search: str = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Transaction]:
        session = get_session()
        try:
            return TransactionRepository(session).get_by_user(
                user_id, start_date, end_date, account_id, category_id, tx_type, search, limit, offset
            )
        finally:
            session.close()

    @staticmethod
    def update_transaction(user_id: int, tx_id: int, data: TransactionUpdate) -> Tuple[bool, str]:
        session = get_session()
        try:
            repo = TransactionRepository(session)
            tx = repo.get_by_id(tx_id)
            if not tx or tx.user_id != user_id or tx.is_deleted:
                return False, "Giao dịch không tồn tại"

            update_data = data.model_dump(exclude_none=True)
            repo.update(tx, update_data)
            AuditRepository(session).log_action(
                user_id, "update_transaction", "transaction", tx_id
            )
            session.commit()
            return True, "Cập nhật giao dịch thành công"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi: {e}"
        finally:
            session.close()

    @staticmethod
    def delete_transaction(user_id: int, tx_id: int) -> Tuple[bool, str]:
        """Xóa mềm giao dịch và hoàn lại số dư."""
        session = get_session()
        try:
            tx_repo = TransactionRepository(session)
            acc_repo = AccountRepository(session)
            tx = tx_repo.get_by_id(tx_id)

            if not tx or tx.user_id != user_id or tx.is_deleted:
                return False, "Giao dịch không tồn tại"

            # Hoàn lại số dư
            if tx.type == "income":
                acc_repo.update_balance(tx.account_id, -tx.amount)
            elif tx.type == "expense":
                acc_repo.update_balance(tx.account_id, tx.amount)
            elif tx.type == "transfer":
                acc_repo.update_balance(tx.account_id, tx.amount)
                if tx.to_account_id:
                    acc_repo.update_balance(tx.to_account_id, -tx.amount)

            tx_repo.soft_delete(tx)
            AuditRepository(session).log_action(
                user_id, "delete_transaction", "transaction", tx_id
            )
            session.commit()
            return True, "Đã xóa giao dịch"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi: {e}"
        finally:
            session.close()

    @staticmethod
    def get_summary(user_id: int, start: datetime, end: datetime) -> dict:
        session = get_session()
        try:
            repo = TransactionRepository(session)
            income = repo.sum_by_type_and_period(user_id, "income", start, end)
            expense = repo.sum_by_type_and_period(user_id, "expense", start, end)
            return {
                "income": income,
                "expense": expense,
                "net": income - expense,
                "saving_rate": round((income - expense) / income * 100, 1) if income > 0 else 0,
            }
        finally:
            session.close()

    @staticmethod
    def get_expense_by_category(user_id: int, start: datetime, end: datetime) -> List:
        session = get_session()
        try:
            return TransactionRepository(session).get_by_category_period(user_id, "expense", start, end)
        finally:
            session.close()

    @staticmethod
    def get_monthly_trend(user_id: int, months: int = 12) -> List:
        session = get_session()
        try:
            return TransactionRepository(session).get_monthly_trend(user_id, months)
        finally:
            session.close()
