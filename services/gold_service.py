"""Gold service - Quản lý giá vàng và nắm giữ vàng.

Provider-based: VNAppMob → DB cache → Manual.
"""

import logging
from typing import List, Optional, Tuple
from datetime import datetime, timezone, date

from db.database import get_session
from models.gold import GoldPrice, GoldHolding
from models.sync_log import SyncLog
from repositories.gold_repo import GoldPriceRepository, GoldHoldingRepository
from repositories.audit_repo import AuditRepository
from services.providers.base import ProviderResult, GoldData
from services.providers.vn_appmob_gold import VNAppMobGoldProvider
from services.providers.manual_provider import ManualGoldProvider
from services.providers.cache_service import cache_service
from config import settings

logger = logging.getLogger(__name__)

_primary = VNAppMobGoldProvider()
_manual = ManualGoldProvider()


class GoldService:
    """Dịch vụ giá vàng và quản lý nắm giữ."""

    # --- Price sync ---

    @staticmethod
    def sync_prices() -> ProviderResult:
        """Đồng bộ giá vàng: primary → db cache → manual."""
        result = _primary.fetch_prices()
        if result.success:
            GoldService._save_prices_to_db(result)
            GoldService._log_sync("vnappmob", "gold", "success", result.message)
            return result

        logger.warning(f"Gold provider chính thất bại: {result.message}")

        db_result = GoldService._load_prices_from_db()
        if db_result.success:
            GoldService._log_sync("db_cache", "gold", "cached", "Dùng cache DB")
            return db_result

        result = _manual.fetch_prices()
        if result.success:
            GoldService._log_sync("manual", "gold", "manual", result.message)
            return result

        return ProviderResult(success=False, source="error", message="Không thể lấy giá vàng")

    @staticmethod
    def get_latest_prices() -> List[dict]:
        session = get_session()
        try:
            prices = GoldPriceRepository(session).get_latest()
            return [
                {
                    "gold_type": p.gold_type,
                    "buy_price": p.buy_price or 0,
                    "sell_price": p.sell_price or 0,
                    "unit": p.unit,
                    "source": p.source,
                    "fetched_at": p.fetched_at,
                }
                for p in prices
            ]
        finally:
            session.close()

    @staticmethod
    def get_price_by_type(gold_type: str) -> Optional[dict]:
        session = get_session()
        try:
            p = GoldPriceRepository(session).get_latest_by_type(gold_type)
            if p:
                return {"buy_price": p.buy_price, "sell_price": p.sell_price, "source": p.source, "fetched_at": p.fetched_at}
            return None
        finally:
            session.close()

    @staticmethod
    def set_manual_prices(prices: dict) -> None:
        _manual.set_prices(prices)

    # --- Holdings ---

    @staticmethod
    def add_holding(user_id: int, gold_type: str, quantity: float, unit: str, buy_price: float, buy_date: date = None, account_id: int = None, notes: str = None) -> Tuple[bool, str]:
        session = get_session()
        try:
            holding = GoldHolding(
                user_id=user_id,
                gold_type=gold_type,
                quantity=quantity,
                unit=unit,
                buy_price=buy_price,
                buy_date=buy_date or date.today(),
                account_id=account_id,
                notes=notes,
            )
            session.add(holding)
            session.flush()
            AuditRepository(session).log_action(user_id, "add_gold", "gold_holding", holding.id)
            session.commit()
            return True, "Thêm vàng thành công"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi: {e}"
        finally:
            session.close()

    @staticmethod
    def get_holdings(user_id: int) -> List[GoldHolding]:
        session = get_session()
        try:
            return GoldHoldingRepository(session).get_by_user(user_id)
        finally:
            session.close()

    @staticmethod
    def delete_holding(user_id: int, holding_id: int) -> Tuple[bool, str]:
        session = get_session()
        try:
            repo = GoldHoldingRepository(session)
            h = repo.get_by_id(holding_id)
            if not h or h.user_id != user_id:
                return False, "Không tìm thấy"
            repo.soft_delete(h)
            AuditRepository(session).log_action(user_id, "delete_gold", "gold_holding", holding_id)
            session.commit()
            return True, "Đã xóa"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi: {e}"
        finally:
            session.close()

    @staticmethod
    def get_total_gold_value(user_id: int) -> float:
        """Tính tổng giá trị vàng quy đổi VND theo giá hiện tại."""
        holdings = GoldService.get_holdings(user_id)
        total = 0.0
        for h in holdings:
            price = GoldService.get_price_by_type(h.gold_type)
            if price and price["sell_price"] > 0:
                total += h.quantity * price["sell_price"]
            else:
                total += h.quantity * h.buy_price  # dùng giá vốn nếu không có giá thị trường
        return total

    @staticmethod
    def get_holdings_with_pnl(user_id: int) -> List[dict]:
        """Danh sách holdings kèm lãi/lỗ tạm tính."""
        holdings = GoldService.get_holdings(user_id)
        result = []
        for h in holdings:
            price = GoldService.get_price_by_type(h.gold_type)
            current_price = price["sell_price"] if price else h.buy_price
            cost = h.quantity * h.buy_price
            market_value = h.quantity * current_price
            pnl = market_value - cost
            result.append({
                "holding": h,
                "current_price": current_price,
                "cost": cost,
                "market_value": market_value,
                "pnl": pnl,
                "pnl_pct": round(pnl / cost * 100, 2) if cost > 0 else 0,
            })
        return result

    # --- Internal ---

    @staticmethod
    def _save_prices_to_db(result: ProviderResult) -> None:
        session = get_session()
        try:
            now = result.fetched_at or datetime.now(timezone.utc)
            for gd in result.data:
                gp = GoldPrice(
                    gold_type=gd.gold_type,
                    buy_price=gd.buy_price,
                    sell_price=gd.sell_price,
                    unit=gd.unit,
                    source=result.source,
                    fetched_at=now,
                )
                session.add(gp)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Lỗi lưu giá vàng: {e}")
        finally:
            session.close()

    @staticmethod
    def _load_prices_from_db() -> ProviderResult:
        session = get_session()
        try:
            prices = GoldPriceRepository(session).get_latest()
            if prices:
                data = [
                    GoldData(gold_type=p.gold_type, buy_price=p.buy_price or 0, sell_price=p.sell_price or 0, unit=p.unit)
                    for p in prices
                ]
                return ProviderResult(
                    success=True, data=data, source="cached",
                    message=f"DB cache: {len(data)} loại vàng",
                    fetched_at=prices[0].fetched_at if prices else None,
                )
            return ProviderResult(success=False, source="cached", message="Không có cache")
        finally:
            session.close()

    @staticmethod
    def _log_sync(provider: str, scope: str, status: str, message: str) -> None:
        session = get_session()
        try:
            session.add(SyncLog(provider=provider, scope=scope, status=status, message=message))
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()

    @staticmethod
    def get_sync_status() -> dict:
        session = get_session()
        try:
            last = session.query(SyncLog).filter(SyncLog.scope == "gold").order_by(SyncLog.created_at.desc()).first()
            if last:
                return {"provider": last.provider, "status": last.status, "message": last.message, "last_sync": last.created_at}
            return {"provider": "none", "status": "never", "message": "Chưa đồng bộ", "last_sync": None}
        finally:
            session.close()
