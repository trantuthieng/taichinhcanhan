"""Account service - Quản lý tài khoản tài chính."""

import logging
from typing import List, Optional, Tuple
from db.database import get_session
from models.account import Account
from repositories.account_repo import AccountRepository
from repositories.audit_repo import AuditRepository
from schemas.account import AccountCreate, AccountUpdate

logger = logging.getLogger(__name__)

ACCOUNT_TYPE_LABELS = {
    "cash": "💵 Tiền mặt",
    "bank": "🏦 Ngân hàng",
    "ewallet": "📱 Ví điện tử",
    "forex": "💱 Ngoại tệ",
    "gold": "🥇 Vàng",
    "savings": "🏧 Tiết kiệm",
    "other": "📋 Khác",
}


class AccountService:
    """Dịch vụ quản lý tài khoản."""

    @staticmethod
    def create_account(user_id: int, data: AccountCreate) -> Tuple[bool, str, Optional[int]]:
        session = get_session()
        try:
            repo = AccountRepository(session)
            account = Account(
                user_id=user_id,
                name=data.name,
                account_type=data.account_type,
                currency=data.currency,
                balance=data.initial_balance,
                initial_balance=data.initial_balance,
                description=data.description,
                bank_name=data.bank_name,
                account_number=data.account_number,
                icon=data.icon or ACCOUNT_TYPE_LABELS.get(data.account_type, "📋").split(" ")[0],
                is_active=1,
            )
            repo.create(account)
            AuditRepository(session).log_action(
                user_id, "create_account", "account", account.id
            )
            session.commit()
            return True, "Tạo tài khoản thành công", account.id
        except Exception as e:
            session.rollback()
            logger.error(f"Lỗi tạo tài khoản: {e}")
            return False, f"Lỗi: {e}", None
        finally:
            session.close()

    @staticmethod
    def get_accounts(user_id: int, include_inactive: bool = False) -> List[Account]:
        session = get_session()
        try:
            return AccountRepository(session).get_by_user(user_id, include_inactive)
        finally:
            session.close()

    @staticmethod
    def get_account(account_id: int) -> Optional[Account]:
        session = get_session()
        try:
            return AccountRepository(session).get_by_id(account_id)
        finally:
            session.close()

    @staticmethod
    def update_account(user_id: int, account_id: int, data: AccountUpdate) -> Tuple[bool, str]:
        session = get_session()
        try:
            repo = AccountRepository(session)
            account = repo.get_by_id(account_id)
            if not account or account.user_id != user_id:
                return False, "Tài khoản không tồn tại"

            update_data = data.model_dump(exclude_none=True)
            repo.update(account, update_data)
            AuditRepository(session).log_action(
                user_id, "update_account", "account", account_id
            )
            session.commit()
            return True, "Cập nhật thành công"
        except Exception as e:
            session.rollback()
            logger.error(f"Lỗi cập nhật tài khoản: {e}")
            return False, f"Lỗi: {e}"
        finally:
            session.close()

    @staticmethod
    def close_account(user_id: int, account_id: int) -> Tuple[bool, str]:
        session = get_session()
        try:
            repo = AccountRepository(session)
            account = repo.get_by_id(account_id)
            if not account or account.user_id != user_id:
                return False, "Tài khoản không tồn tại"
            account.is_active = 0
            AuditRepository(session).log_action(
                user_id, "close_account", "account", account_id
            )
            session.commit()
            return True, "Đã đóng tài khoản"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi: {e}"
        finally:
            session.close()

    @staticmethod
    def adjust_balance(user_id: int, account_id: int, new_balance: float) -> Tuple[bool, str]:
        session = get_session()
        try:
            repo = AccountRepository(session)
            account = repo.get_by_id(account_id)
            if not account or account.user_id != user_id:
                return False, "Tài khoản không tồn tại"
            old_balance = account.balance
            account.balance = new_balance
            AuditRepository(session).log_action(
                user_id, "adjust_balance", "account", account_id,
                old_value={"balance": old_balance},
                new_value={"balance": new_balance},
            )
            session.commit()
            return True, f"Đã điều chỉnh số dư từ {old_balance:,.0f} → {new_balance:,.0f}"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi: {e}"
        finally:
            session.close()

    @staticmethod
    def get_total_balance(user_id: int) -> dict:
        session = get_session()
        try:
            return AccountRepository(session).get_total_balance_by_currency(user_id)
        finally:
            session.close()

    @staticmethod
    def get_accounts_by_type(user_id: int, account_type: str) -> List[Account]:
        session = get_session()
        try:
            return AccountRepository(session).get_by_user_and_type(user_id, account_type)
        finally:
            session.close()
