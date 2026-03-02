"""VNAppMob Exchange Rate Provider.

Nguồn chính cho tỷ giá ngoại tệ.
Tự động xử lý token, retry 403, fallback.
"""

import logging
import time
from datetime import datetime, timezone
from typing import List
import requests

from config import settings
from services.providers.base import BaseRateProvider, RateData, ProviderResult
from services.providers.token_manager import token_manager
from services.providers.cache_service import cache_service

logger = logging.getLogger(__name__)

CACHE_KEY = "vnappmob_exchange_rates"


class VNAppMobExchangeProvider(BaseRateProvider):
    """Provider tỷ giá từ VNAppMob API."""

    @property
    def name(self) -> str:
        return "vnappmob"

    def fetch_rates(self) -> ProviderResult:
        """Lấy tỷ giá, tự xử lý token và retry."""
        # Kiểm tra cache in-memory trước
        cached = cache_service.get(CACHE_KEY)
        if cached:
            logger.debug("Trả tỷ giá từ memory cache.")
            return ProviderResult(
                success=True,
                data=cached,
                source="cached",
                message="Dữ liệu từ cache",
                fetched_at=cache_service.get_created_at(CACHE_KEY),
            )

        # Lấy token
        scope = settings.VNAPPMOB_EXCHANGE_SCOPE
        token = token_manager.get_token(scope)
        if not token:
            logger.warning("Không thể lấy token cho exchange_rate")
            return ProviderResult(success=False, source="error", message="Không thể lấy API token")

        # Gọi API
        result = self._call_api(token, scope)
        if result.success:
            cache_service.set(CACHE_KEY, result.data, settings.RATE_CACHE_TTL)
        return result

    def _call_api(self, token: str, scope: str) -> ProviderResult:
        """Gọi VNAppMob exchange rate API."""
        url = f"{settings.VNAPPMOB_BASE_URL}/v2/exchange_rate/vcb"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            start = time.time()
            resp = requests.get(url, headers=headers, timeout=15)
            elapsed = (time.time() - start) * 1000

            if resp.status_code == 200:
                return self._parse_response(resp.json(), elapsed)

            if resp.status_code == 403:
                logger.warning("Token bị từ chối (403), đang refresh...")
                new_token = token_manager.force_refresh(scope)
                if new_token:
                    return self._retry_with_token(new_token)
                return ProviderResult(
                    success=False, source="error", message="Token 403 và refresh thất bại"
                )

            return ProviderResult(
                success=False, source="error", message=f"HTTP {resp.status_code}"
            )

        except requests.Timeout:
            logger.error("Timeout khi gọi VNAppMob exchange rate API")
            return ProviderResult(success=False, source="error", message="API timeout")
        except requests.RequestException as e:
            logger.error(f"Lỗi kết nối VNAppMob: {e}")
            return ProviderResult(success=False, source="error", message=str(e))

    def _retry_with_token(self, token: str) -> ProviderResult:
        """Retry 1 lần với token mới."""
        url = f"{settings.VNAPPMOB_BASE_URL}/v2/exchange_rate/vcb"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            start = time.time()
            resp = requests.get(url, headers=headers, timeout=15)
            elapsed = (time.time() - start) * 1000

            if resp.status_code == 200:
                result = self._parse_response(resp.json(), elapsed)
                result.source = "refreshed_token"
                return result

            return ProviderResult(
                success=False, source="error", message=f"Retry thất bại: HTTP {resp.status_code}"
            )
        except requests.RequestException as e:
            return ProviderResult(success=False, source="error", message=f"Retry lỗi: {e}")

    def _parse_response(self, data: dict, elapsed_ms: float) -> ProviderResult:
        """Parse JSON response thành list RateData."""
        results = data.get("results", [])
        rates: List[RateData] = []

        for item in results:
            try:
                rates.append(
                    RateData(
                        currency_code=item.get("currency_code", ""),
                        currency_name=item.get("currency_name", ""),
                        buy_rate=self._parse_float(item.get("buy", "0")),
                        sell_rate=self._parse_float(item.get("sell", "0")),
                        transfer_rate=self._parse_float(item.get("transfer", "0")),
                    )
                )
            except (ValueError, KeyError) as e:
                logger.warning(f"Bỏ qua rate lỗi: {e}")

        now = datetime.now(timezone.utc)
        return ProviderResult(
            success=True,
            data=rates,
            source="realtime",
            message=f"Lấy {len(rates)} tỷ giá trong {elapsed_ms:.0f}ms",
            fetched_at=now,
        )

    @staticmethod
    def _parse_float(val) -> float:
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            val = val.replace(",", "").strip()
            return float(val) if val else 0.0
        return 0.0
