"""Report service - Báo cáo tài chính."""

import logging
import io
from typing import Optional
from datetime import datetime, date

import pandas as pd
from sqlalchemy import func, cast, Date, String

from db.database import get_session, get_active_database_url
from models.transaction import Transaction
from models.account import Account
from models.category import Category, SubCategory

logger = logging.getLogger(__name__)


def _is_pg():
    return get_active_database_url().startswith("postgresql")


def _month_label(col):
    """Return a cross-DB 'YYYY-MM' expression."""
    if _is_pg():
        return func.to_char(col, 'YYYY-MM').label("month")
    return func.strftime("%Y-%m", col).label("month")


def _date_label(col):
    """Return a cross-DB date-only expression."""
    if _is_pg():
        return cast(col, Date).label("day")
    return func.date(col).label("day")


class ReportService:
    """Dịch vụ báo cáo & xuất file."""

    @staticmethod
    def get_income_expense_summary(user_id: int, start: datetime, end: datetime) -> dict:
        """Thu nhập / Chi tiêu trong khoảng thời gian."""
        session = get_session()
        try:
            rows = (
                session.query(Transaction.type, func.sum(Transaction.amount))
                .filter(
                    Transaction.user_id == user_id,
                    Transaction.is_deleted == 0,
                    Transaction.status == "completed",
                    Transaction.transaction_date >= start,
                    Transaction.transaction_date < end,
                )
                .group_by(Transaction.type)
                .all()
            )
            result = {"income": 0, "expense": 0, "transfer": 0}
            for r in rows:
                result[r[0]] = float(r[1] or 0)
            result["net"] = result["income"] - result["expense"]
            return result
        finally:
            session.close()

    @staticmethod
    def get_expense_by_category(user_id: int, start: datetime, end: datetime) -> list:
        """Chi tiêu nhóm theo danh mục."""
        session = get_session()
        try:
            rows = (
                session.query(
                    Category.name,
                    func.sum(Transaction.amount).label("total"),
                )
                .join(SubCategory, SubCategory.id == Transaction.category_id)
                .join(Category, Category.id == SubCategory.category_id)
                .filter(
                    Transaction.user_id == user_id,
                    Transaction.type == "expense",
                    Transaction.is_deleted == 0,
                    Transaction.status == "completed",
                    Transaction.transaction_date >= start,
                    Transaction.transaction_date < end,
                )
                .group_by(Category.name)
                .order_by(func.sum(Transaction.amount).desc())
                .all()
            )
            return [{"category": r[0], "total": float(r[1])} for r in rows]
        finally:
            session.close()

    @staticmethod
    def get_expense_by_subcategory(user_id: int, start: datetime, end: datetime) -> list:
        """Chi tiêu nhóm theo danh mục con."""
        session = get_session()
        try:
            rows = (
                session.query(
                    Category.name.label("cat"),
                    SubCategory.name.label("sub"),
                    func.sum(Transaction.amount).label("total"),
                )
                .join(SubCategory, SubCategory.id == Transaction.category_id)
                .join(Category, Category.id == SubCategory.category_id)
                .filter(
                    Transaction.user_id == user_id,
                    Transaction.type == "expense",
                    Transaction.is_deleted == 0,
                    Transaction.status == "completed",
                    Transaction.transaction_date >= start,
                    Transaction.transaction_date < end,
                )
                .group_by(Category.name, SubCategory.name)
                .order_by(func.sum(Transaction.amount).desc())
                .all()
            )
            return [{"category": r[0], "subcategory": r[1], "total": float(r[2])} for r in rows]
        finally:
            session.close()

    @staticmethod
    def get_monthly_trend(user_id: int, months: int = 12) -> list:
        """Xu hướng thu chi 12 tháng gần nhất."""
        session = get_session()
        try:
            from dateutil.relativedelta import relativedelta
            end = datetime.now()
            start = end - relativedelta(months=months)

            month_col = _month_label(Transaction.transaction_date)
            rows = (
                session.query(
                    month_col,
                    Transaction.type,
                    func.sum(Transaction.amount).label("total"),
                )
                .filter(
                    Transaction.user_id == user_id,
                    Transaction.is_deleted == 0,
                    Transaction.status == "completed",
                    Transaction.transaction_date >= start,
                )
                .group_by(month_col, Transaction.type)
                .order_by(month_col)
                .all()
            )

            trend_map = {}
            for r in rows:
                m = r[0]
                if m not in trend_map:
                    trend_map[m] = {"month": m, "income": 0, "expense": 0}
                trend_map[m][r[1]] = float(r[2] or 0)

            trend = list(trend_map.values())
            for t in trend:
                t["net"] = t["income"] - t["expense"]
            return trend
        finally:
            session.close()

    @staticmethod
    def get_daily_expenses(user_id: int, start: datetime, end: datetime) -> list:
        """Chi tiêu theo ngày."""
        session = get_session()
        try:
            day_col = _date_label(Transaction.transaction_date)
            rows = (
                session.query(
                    day_col,
                    func.sum(Transaction.amount).label("total"),
                )
                .filter(
                    Transaction.user_id == user_id,
                    Transaction.type == "expense",
                    Transaction.is_deleted == 0,
                    Transaction.status == "completed",
                    Transaction.transaction_date >= start,
                    Transaction.transaction_date < end,
                )
                .group_by(day_col)
                .order_by(day_col)
                .all()
            )
            return [{"date": r[0], "total": float(r[1])} for r in rows]
        finally:
            session.close()

    @staticmethod
    def get_account_balances(user_id: int) -> list:
        """Số dư các tài khoản."""
        session = get_session()
        try:
            accounts = session.query(Account).filter(
                Account.user_id == user_id, Account.is_deleted == 0
            ).all()
            return [
                {"name": a.name, "type": a.type, "currency": a.currency, "balance": float(a.balance)}
                for a in accounts
            ]
        finally:
            session.close()

    @staticmethod
    def export_transactions_excel(user_id: int, start: datetime, end: datetime) -> bytes:
        """Xuất giao dịch ra file Excel."""
        session = get_session()
        try:
            txs = (
                session.query(Transaction)
                .filter(
                    Transaction.user_id == user_id,
                    Transaction.is_deleted == 0,
                    Transaction.transaction_date >= start,
                    Transaction.transaction_date < end,
                )
                .order_by(Transaction.transaction_date.desc())
                .all()
            )

            # Load references
            accounts = {a.id: a.name for a in session.query(Account).filter(Account.user_id == user_id).all()}
            subcategories = {s.id: s.name for s in session.query(SubCategory).all()}

            rows_data = []
            for t in txs:
                rows_data.append({
                    "Ngày": t.transaction_date.strftime("%Y-%m-%d %H:%M") if t.transaction_date else "",
                    "Loại": {"income": "Thu nhập", "expense": "Chi tiêu", "transfer": "Chuyển khoản"}.get(t.type, t.type),
                    "Số tiền": t.amount,
                    "Tài khoản": accounts.get(t.account_id, ""),
                    "Danh mục": subcategories.get(t.category_id, ""),
                    "Ghi chú": t.description or "",
                    "Trạng thái": t.status,
                })

            df = pd.DataFrame(rows_data)
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Giao dịch")
                ws = writer.sheets["Giao dịch"]
                ws.set_column("A:A", 18)
                ws.set_column("B:B", 12)
                ws.set_column("C:C", 15)
                ws.set_column("D:D", 20)
                ws.set_column("E:E", 20)
                ws.set_column("F:F", 30)
            return buf.getvalue()
        finally:
            session.close()

    @staticmethod
    def export_transactions_csv(user_id: int, start: datetime, end: datetime) -> str:
        """Xuất giao dịch ra CSV."""
        session = get_session()
        try:
            txs = (
                session.query(Transaction)
                .filter(
                    Transaction.user_id == user_id,
                    Transaction.is_deleted == 0,
                    Transaction.transaction_date >= start,
                    Transaction.transaction_date < end,
                )
                .order_by(Transaction.transaction_date.desc())
                .all()
            )

            accounts = {a.id: a.name for a in session.query(Account).filter(Account.user_id == user_id).all()}
            subcategories = {s.id: s.name for s in session.query(SubCategory).all()}

            rows_data = []
            for t in txs:
                rows_data.append({
                    "Ngày": t.transaction_date.strftime("%Y-%m-%d %H:%M") if t.transaction_date else "",
                    "Loại": t.type,
                    "Số tiền": t.amount,
                    "Tài khoản": accounts.get(t.account_id, ""),
                    "Danh mục": subcategories.get(t.category_id, ""),
                    "Ghi chú": t.description or "",
                })

            df = pd.DataFrame(rows_data)
            return df.to_csv(index=False)
        finally:
            session.close()
