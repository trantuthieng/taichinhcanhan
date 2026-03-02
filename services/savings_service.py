"""Savings service - Quản lý tiền gửi tiết kiệm."""

import logging
from typing import List, Optional, Tuple
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from db.database import get_session
from models.savings import SavingsDeposit, SavingsInterestEvent
from repositories.savings_repo import SavingsRepository, SavingsInterestEventRepository
from repositories.audit_repo import AuditRepository
from schemas.savings import SavingsDepositCreate

logger = logging.getLogger(__name__)


def _calc_maturity_date(open_date: date, term_months: int) -> date:
    """Tính ngày đáo hạn."""
    return open_date + relativedelta(months=term_months)


def _calc_expected_interest(principal: float, rate: float, term_months: int, interest_type: str, compound: bool, tax_rate: float = 0.0) -> dict:
    """Tính lãi dự kiến.

    rate: lãi suất %/năm
    """
    annual_rate = rate / 100.0
    days = term_months * 30  # xấp xỉ

    if interest_type == "prepaid":
        # Trả lãi trước: lãi tính trên gốc
        gross_interest = principal * annual_rate * days / 365
        tax = gross_interest * (tax_rate / 100.0) if term_months > 6 else 0.0
        net_interest = gross_interest - tax
        total = principal  # Gốc nhận đủ, lãi đã nhận trước
        return {"gross_interest": gross_interest, "tax": tax, "net_interest": net_interest, "total_at_maturity": total + net_interest}

    elif interest_type == "monthly":
        # Trả lãi hàng tháng
        monthly_interest = principal * annual_rate / 12
        gross_interest = monthly_interest * term_months
        tax = gross_interest * (tax_rate / 100.0) if term_months > 6 else 0.0
        net_interest = gross_interest - tax
        return {"gross_interest": gross_interest, "tax": tax, "net_interest": net_interest, "total_at_maturity": principal, "monthly_interest": monthly_interest}

    else:  # maturity
        if compound:
            # Lãi nhập gốc hàng tháng
            balance = principal
            for _ in range(term_months):
                balance *= (1 + annual_rate / 12)
            gross_interest = balance - principal
        else:
            gross_interest = principal * annual_rate * days / 365

        tax = gross_interest * (tax_rate / 100.0) if term_months > 6 else 0.0
        net_interest = gross_interest - tax
        total = principal + net_interest
        return {"gross_interest": gross_interest, "tax": tax, "net_interest": net_interest, "total_at_maturity": total}


class SavingsService:
    """Dịch vụ tiết kiệm."""

    @staticmethod
    def create_deposit(user_id: int, data: SavingsDepositCreate) -> Tuple[bool, str, Optional[int]]:
        session = get_session()
        try:
            maturity = _calc_maturity_date(data.open_date, data.term_months)
            deposit = SavingsDeposit(
                user_id=user_id,
                account_id=data.account_id,
                bank_name=data.bank_name,
                principal_amount=data.principal_amount,
                currency=data.currency,
                open_date=data.open_date,
                term_months=data.term_months,
                maturity_date=maturity,
                interest_rate=data.interest_rate,
                interest_type=data.interest_type,
                compound_interest=1 if data.compound_interest else 0,
                auto_renew=1 if data.auto_renew else 0,
                status="active",
                tax_rate=data.tax_rate,
                fee=data.fee,
                notes=data.notes,
            )
            session.add(deposit)
            session.flush()
            AuditRepository(session).log_action(user_id, "create_savings", "savings_deposit", deposit.id)
            session.commit()
            return True, "Mở sổ tiết kiệm thành công", deposit.id
        except Exception as e:
            session.rollback()
            logger.error(f"Lỗi tạo tiết kiệm: {e}")
            return False, f"Lỗi: {e}", None
        finally:
            session.close()

    @staticmethod
    def get_deposits(user_id: int, status: str = None) -> List[SavingsDeposit]:
        session = get_session()
        try:
            return SavingsRepository(session).get_by_user(user_id, status)
        finally:
            session.close()

    @staticmethod
    def get_active_deposits(user_id: int) -> List[SavingsDeposit]:
        return SavingsService.get_deposits(user_id, "active")

    @staticmethod
    def get_deposit_detail(deposit_id: int) -> Optional[dict]:
        """Chi tiết sổ tiết kiệm kèm tính toán lãi."""
        session = get_session()
        try:
            repo = SavingsRepository(session)
            d = repo.get_by_id(deposit_id)
            if not d:
                return None

            today = date.today()
            days_remaining = max(0, (d.maturity_date - today).days) if d.status == "active" else 0
            is_overdue = d.maturity_date < today and d.status == "active"

            interest_info = _calc_expected_interest(
                d.principal_amount, d.interest_rate, d.term_months,
                d.interest_type, bool(d.compound_interest), d.tax_rate,
            )

            events = SavingsInterestEventRepository(session).get_by_savings(deposit_id)

            return {
                "deposit": d,
                "days_remaining": days_remaining,
                "is_overdue": is_overdue,
                "interest": interest_info,
                "events": events,
            }
        finally:
            session.close()

    @staticmethod
    def close_deposit(user_id: int, deposit_id: int, early: bool = False) -> Tuple[bool, str]:
        """Tất toán sổ tiết kiệm."""
        session = get_session()
        try:
            repo = SavingsRepository(session)
            d = repo.get_by_id(deposit_id)
            if not d or d.user_id != user_id:
                return False, "Không tìm thấy sổ tiết kiệm"

            event_type = "early_close" if early else "maturity"
            interest_info = _calc_expected_interest(
                d.principal_amount, d.interest_rate, d.term_months,
                d.interest_type, bool(d.compound_interest), d.tax_rate,
            )

            event = SavingsInterestEvent(
                savings_id=deposit_id,
                event_type=event_type,
                amount=interest_info["net_interest"],
                event_date=date.today(),
                notes="Tất toán sớm" if early else "Đáo hạn",
            )
            session.add(event)
            d.status = "closed"

            AuditRepository(session).log_action(user_id, "close_savings", "savings_deposit", deposit_id)
            session.commit()
            return True, "Tất toán thành công"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi: {e}"
        finally:
            session.close()

    @staticmethod
    def renew_deposit(user_id: int, deposit_id: int) -> Tuple[bool, str]:
        """Tái tục sổ tiết kiệm."""
        session = get_session()
        try:
            repo = SavingsRepository(session)
            d = repo.get_by_id(deposit_id)
            if not d or d.user_id != user_id:
                return False, "Không tìm thấy sổ tiết kiệm"

            # Ghi nhận event
            interest_info = _calc_expected_interest(
                d.principal_amount, d.interest_rate, d.term_months,
                d.interest_type, bool(d.compound_interest), d.tax_rate,
            )
            event = SavingsInterestEvent(
                savings_id=deposit_id,
                event_type="renewal",
                amount=interest_info["net_interest"],
                event_date=date.today(),
            )
            session.add(event)

            # Cập nhật sổ
            d.status = "renewed"

            # Tạo sổ mới
            new_open = date.today()
            new_maturity = _calc_maturity_date(new_open, d.term_months)
            new_principal = d.principal_amount
            if d.compound_interest:
                new_principal += interest_info["net_interest"]

            new_deposit = SavingsDeposit(
                user_id=user_id,
                account_id=d.account_id,
                bank_name=d.bank_name,
                principal_amount=new_principal,
                currency=d.currency,
                open_date=new_open,
                term_months=d.term_months,
                maturity_date=new_maturity,
                interest_rate=d.interest_rate,
                interest_type=d.interest_type,
                compound_interest=d.compound_interest,
                auto_renew=d.auto_renew,
                status="active",
                tax_rate=d.tax_rate,
                fee=d.fee,
                notes=f"Tái tục từ sổ #{deposit_id}",
            )
            session.add(new_deposit)
            AuditRepository(session).log_action(user_id, "renew_savings", "savings_deposit", deposit_id)
            session.commit()
            return True, f"Tái tục thành công. Gốc mới: {new_principal:,.0f}"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi: {e}"
        finally:
            session.close()

    @staticmethod
    def get_total_savings(user_id: int) -> float:
        session = get_session()
        try:
            return SavingsRepository(session).get_total_principal(user_id)
        finally:
            session.close()

    @staticmethod
    def get_maturing_soon(user_id: int, days: int = 30) -> List[SavingsDeposit]:
        session = get_session()
        try:
            return SavingsRepository(session).get_maturing_soon(user_id, days)
        finally:
            session.close()

    @staticmethod
    def get_overdue(user_id: int) -> List[SavingsDeposit]:
        session = get_session()
        try:
            return SavingsRepository(session).get_overdue(user_id)
        finally:
            session.close()
