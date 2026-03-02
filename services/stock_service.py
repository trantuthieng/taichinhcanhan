"""Stock service - Quản lý danh mục chứng khoán."""

import logging
from typing import List, Optional, Tuple
from datetime import date

from db.database import get_session
from models.stock import StockHolding
from repositories.stock_repo import StockHoldingRepository
from repositories.audit_repo import AuditRepository

logger = logging.getLogger(__name__)


class StockService:
    """Dịch vụ CRUD & tổng hợp chứng khoán."""

    # ---------- Holdings CRUD ----------

    @staticmethod
    def add_holding(
        user_id: int,
        ticker: str,
        quantity: float,
        avg_price: float,
        name: Optional[str] = None,
        exchange: str = "HOSE",
        current_price: Optional[float] = None,
        buy_date: Optional[date] = None,
        account_id: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> Tuple[bool, str]:
        session = get_session()
        try:
            holding = StockHolding(
                user_id=user_id,
                ticker=ticker.upper().strip(),
                name=name,
                exchange=exchange,
                quantity=quantity,
                avg_price=avg_price,
                current_price=current_price,
                buy_date=buy_date,
                account_id=account_id,
                notes=notes,
            )
            StockHoldingRepository(session).create(holding)
            AuditRepository(session).log_action(user_id, "create_stock", "stock_holding", holding.id)
            session.commit()
            return True, f"Đã thêm {quantity} CP {ticker.upper()}"
        except Exception as e:
            session.rollback()
            logger.error(f"Lỗi thêm cổ phiếu: {e}")
            return False, str(e)
        finally:
            session.close()

    @staticmethod
    def update_holding(user_id: int, holding_id: int, data: dict) -> Tuple[bool, str]:
        session = get_session()
        try:
            repo = StockHoldingRepository(session)
            holding = repo.get_by_id(holding_id)
            if not holding or holding.user_id != user_id or holding.is_deleted == 1:
                return False, "Không tìm thấy khoản nắm giữ"
            repo.update(holding, data)
            AuditRepository(session).log_action(user_id, "update_stock", "stock_holding", holding_id)
            session.commit()
            return True, "Đã cập nhật"
        except Exception as e:
            session.rollback()
            logger.error(f"Lỗi cập nhật cổ phiếu: {e}")
            return False, str(e)
        finally:
            session.close()

    @staticmethod
    def delete_holding(user_id: int, holding_id: int) -> Tuple[bool, str]:
        session = get_session()
        try:
            repo = StockHoldingRepository(session)
            holding = repo.get_by_id(holding_id)
            if not holding or holding.user_id != user_id:
                return False, "Không tìm thấy"
            repo.soft_delete(holding)
            AuditRepository(session).log_action(user_id, "delete_stock", "stock_holding", holding_id)
            session.commit()
            return True, "Đã xoá"
        except Exception as e:
            session.rollback()
            logger.error(f"Lỗi xoá cổ phiếu: {e}")
            return False, str(e)
        finally:
            session.close()

    @staticmethod
    def get_holdings(user_id: int) -> List[StockHolding]:
        session = get_session()
        try:
            return StockHoldingRepository(session).get_by_user(user_id)
        finally:
            session.close()

    @staticmethod
    def get_portfolio_summary(user_id: int) -> List[dict]:
        session = get_session()
        try:
            return StockHoldingRepository(session).get_portfolio_summary(user_id)
        finally:
            session.close()

    @staticmethod
    def update_prices(user_id: int, price_map: dict[str, float]) -> Tuple[bool, str]:
        """Cập nhật giá thị trường hàng loạt.

        price_map: {"VNM": 72000, "FPT": 120000, ...}
        """
        session = get_session()
        try:
            repo = StockHoldingRepository(session)
            holdings = repo.get_by_user(user_id)
            updated = 0
            for h in holdings:
                tk = h.ticker.upper()
                if tk in price_map:
                    h.current_price = price_map[tk]
                    updated += 1
            session.commit()
            return True, f"Đã cập nhật giá cho {updated} khoản"
        except Exception as e:
            session.rollback()
            logger.error(f"Lỗi cập nhật giá CK: {e}")
            return False, str(e)
        finally:
            session.close()

    @staticmethod
    def get_total_portfolio_value(user_id: int) -> dict:
        """Trả về tổng giá trị, tổng vốn, lãi/lỗ."""
        summary = StockService.get_portfolio_summary(user_id)
        total_cost = sum(s["cost"] for s in summary)
        total_mv = sum(s["market_value"] for s in summary)
        profit = total_mv - total_cost
        pct = (profit / total_cost * 100) if total_cost else 0
        return {
            "total_cost": total_cost,
            "total_market_value": total_mv,
            "total_profit": profit,
            "profit_pct": pct,
            "count": len(summary),
        }
