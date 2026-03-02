"""VNAppMob Gold Price Provider.

Nguồn chính cho giá vàng.
"""

import logging
import time
from datetime import datetime, timezone
from typing import List
import requests

from config import settings
from services.providers.base import BaseGoldProvider, GoldData, ProviderResult
from services.providers.token_manager import token_manager
from services.providers.cache_service import cache_service

logger = logging.getLogger(__name__)

CACHE_KEY = "vnappmob_gold_prices"


class VNAppMobGoldProvider(BaseGoldProvider):
    """Provider giá vàng từ VNAppMob API."""

    @property
    def name(self) -> str:
        return "vnappmob"

    def fetch_prices(self) -> ProviderResult:
        """Lấy giá vàng, tự xử lý token và retry."""
        cached = cache_service.get(CACHE_KEY)
        if cached:
            return ProviderResult(
                success=True,
                data=cached,
                source="cached",
                message="Dữ liệu từ cache",
                fetched_at=cache_service.get_created_at(CACHE_KEY),
            )

        scope = settings.VNAPPMOB_GOLD_SCOPE
        token = token_manager.get_token(scope)
        if not token:
            return ProviderResult(success=False, source="error", message="Không thể lấy API token")

        result = self._call_api(token, scope)
        if result.success:
            cache_service.set(CACHE_KEY, result.data, settings.GOLD_CACHE_TTL)
        return result

    def _call_api(self, token: str, scope: str) -> ProviderResult:
        url = f"{settings.VNAPPMOB_BASE_URL}/v2/gold/sjc"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            start = time.time()
            resp = requests.get(url, headers=headers, timeout=15)
            elapsed = (time.time() - start) * 1000

            if resp.status_code == 200:
                return self._parse_response(resp.json(), elapsed)

            if resp.status_code == 403:
                logger.warning("Gold token 403, đang refresh...")
                new_token = token_manager.force_refresh(scope)
                if new_token:
                    return self._retry_with_token(new_token)
                return ProviderResult(success=False, source="error", message="Token 403 + refresh thất bại")

            return ProviderResult(success=False, source="error", message=f"HTTP {resp.status_code}")

        except requests.Timeout:
            return ProviderResult(success=False, source="error", message="API timeout")
        except requests.RequestException as e:
            return ProviderResult(success=False, source="error", message=str(e))

    def _retry_with_token(self, token: str) -> ProviderResult:
        url = f"{settings.VNAPPMOB_BASE_URL}/v2/gold/sjc"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            start = time.time()
            resp = requests.get(url, headers=headers, timeout=15)
            elapsed = (time.time() - start) * 1000
            if resp.status_code == 200:
                result = self._parse_response(resp.json(), elapsed)
                result.source = "refreshed_token"
                return result
            return ProviderResult(success=False, source="error", message=f"Retry thất bại: {resp.status_code}")
        except requests.RequestException as e:
            return ProviderResult(success=False, source="error", message=f"Retry lỗi: {e}")

    def _parse_response(self, data: dict, elapsed_ms: float) -> ProviderResult:
        results = data.get("results", [])
        prices: List[GoldData] = []
        for item in results:
            try:
                prices.append(
                    GoldData(
                        gold_type=item.get("type", "SJC"),
                        buy_price=self._parse_float(item.get("buy", "0")),
                        sell_price=self._parse_float(item.get("sell", "0")),
                        unit="lượng",
                    )
                )
            except (ValueError, KeyError) as e:
                logger.warning(f"Bỏ qua gold data lỗi: {e}")

        return ProviderResult(
            success=True,
            data=prices,
            source="realtime",
            message=f"Lấy {len(prices)} loại vàng trong {elapsed_ms:.0f}ms",
            fetched_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def _parse_float(val) -> float:
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            val = val.replace(",", "").strip()
            return float(val) if val else 0.0
        return 0.0
