"""FX service - Quản lý tỷ giá ngoại tệ.

Kiến trúc provider-based với fallback chain:
VNAppMob → Vietcombank XML → DB cache → Manual
"""

import logging
from typing import List, Optional, Tuple
from datetime import datetime, timezone

from db.database import get_session
from models.fx_rate import FxRate
from models.sync_log import SyncLog
from repositories.fx_repo import FxRateRepository
from services.providers.base import ProviderResult, RateData
from services.providers.vn_appmob_exchange import VNAppMobExchangeProvider
from services.providers.vietcombank_fallback import VietcombankXmlFallbackProvider
from services.providers.manual_provider import ManualRateProvider
from services.providers.cache_service import cache_service
from config import settings

logger = logging.getLogger(__name__)

# Singleton providers
_primary = VNAppMobExchangeProvider()
_fallback = VietcombankXmlFallbackProvider()
_manual = ManualRateProvider()


class FxService:
    """Dịch vụ tỷ giá ngoại tệ với fallback chain."""

    @staticmethod
    def sync_rates() -> ProviderResult:
        """Đồng bộ tỷ giá: primary → fallback → db cache → manual."""
        # 1. Thử provider chính
        result = _primary.fetch_rates()
        if result.success:
            FxService._save_to_db(result)
            FxService._log_sync("vnappmob", "exchange_rate", "success", result.message)
            return result

        logger.warning(f"Provider chính thất bại: {result.message}")

        # 2. Thử fallback provider
        result = _fallback.fetch_rates()
        if result.success:
            FxService._save_to_db(result)
            FxService._log_sync("vietcombank", "exchange_rate", "fallback", result.message)
            return result

        logger.warning(f"Fallback thất bại: {result.message}")

        # 3. Thử DB cache
        db_result = FxService._load_from_db()
        if db_result.success:
            FxService._log_sync("db_cache", "exchange_rate", "cached", "Dùng dữ liệu cache từ DB")
            return db_result

        # 4. Cuối cùng: manual
        result = _manual.fetch_rates()
        if result.success:
            FxService._log_sync("manual", "exchange_rate", "manual", result.message)
            return result

        return ProviderResult(
            success=False,
            source="error",
            message="Không thể lấy tỷ giá từ bất kỳ nguồn nào",
        )

    @staticmethod
    def get_latest_rates() -> List[dict]:
        """Lấy tỷ giá mới nhất từ DB."""
        session = get_session()
        try:
            repo = FxRateRepository(session)
            rates = repo.get_latest()
            return [
                {
                    "currency_code": r.currency_code,
                    "currency_name": r.currency_name or r.currency_code,
                    "buy_rate": r.buy_rate or 0,
                    "sell_rate": r.sell_rate or 0,
                    "transfer_rate": r.transfer_rate or 0,
                    "source": r.source,
                    "fetched_at": r.fetched_at,
                }
                for r in rates
            ]
        finally:
            session.close()

    @staticmethod
    def get_rate(currency_code: str) -> Optional[dict]:
        """Lấy tỷ giá 1 loại tiền."""
        session = get_session()
        try:
            rate = FxRateRepository(session).get_latest_single(currency_code)
            if rate:
                return {
                    "buy_rate": rate.buy_rate or 0,
                    "sell_rate": rate.sell_rate or 0,
                    "transfer_rate": rate.transfer_rate or 0,
                    "source": rate.source,
                    "fetched_at": rate.fetched_at,
                }
            return None
        finally:
            session.close()

    @staticmethod
    def convert_to_vnd(amount: float, currency_code: str) -> float:
        """Quy đổi số tiền sang VND."""
        if currency_code == "VND":
            return amount
        rate = FxService.get_rate(currency_code)
        if rate and rate["sell_rate"] > 0:
            return amount * rate["sell_rate"]
        return 0.0

    @staticmethod
    def set_manual_rates(rates: dict) -> None:
        """Cập nhật tỷ giá nhập tay."""
        _manual.set_rates(rates)

    @staticmethod
    def _save_to_db(result: ProviderResult) -> None:
        """Lưu tỷ giá vào DB."""
        session = get_session()
        try:
            now = result.fetched_at or datetime.now(timezone.utc)
            repo = FxRateRepository(session)
            for rate_data in result.data:
                rate = FxRate(
                    currency_code=rate_data.currency_code,
                    currency_name=rate_data.currency_name,
                    buy_rate=rate_data.buy_rate,
                    sell_rate=rate_data.sell_rate,
                    transfer_rate=rate_data.transfer_rate,
                    source=result.source,
                    fetched_at=now,
                )
                session.add(rate)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Lỗi lưu tỷ giá: {e}")
        finally:
            session.close()

    @staticmethod
    def _load_from_db() -> ProviderResult:
        """Load tỷ giá từ DB cache."""
        session = get_session()
        try:
            rates = FxRateRepository(session).get_latest()
            if rates:
                data = [
                    RateData(
                        currency_code=r.currency_code,
                        currency_name=r.currency_name or "",
                        buy_rate=r.buy_rate or 0,
                        sell_rate=r.sell_rate or 0,
                        transfer_rate=r.transfer_rate or 0,
                    )
                    for r in rates
                ]
                return ProviderResult(
                    success=True,
                    data=data,
                    source="cached",
                    message=f"DB cache: {len(data)} tỷ giá",
                    fetched_at=rates[0].fetched_at if rates else None,
                )
            return ProviderResult(success=False, source="cached", message="Không có dữ liệu cache")
        finally:
            session.close()

    @staticmethod
    def _log_sync(provider: str, scope: str, status: str, message: str) -> None:
        session = get_session()
        try:
            log = SyncLog(provider=provider, scope=scope, status=status, message=message)
            session.add(log)
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()

    @staticmethod
    def get_sync_status() -> dict:
        """Trạng thái đồng bộ tỷ giá."""
        session = get_session()
        try:
            last = (
                session.query(SyncLog)
                .filter(SyncLog.scope == "exchange_rate")
                .order_by(SyncLog.created_at.desc())
                .first()
            )
            if last:
                return {
                    "provider": last.provider,
                    "status": last.status,
                    "message": last.message,
                    "last_sync": last.created_at,
                }
            return {"provider": "none", "status": "never", "message": "Chưa đồng bộ", "last_sync": None}
        finally:
            session.close()
