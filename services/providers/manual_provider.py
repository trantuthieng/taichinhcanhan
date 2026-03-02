"""Manual Rate/Gold Provider.

Cho phép nhập tỷ giá và giá vàng thủ công từ settings.
Dùng khi tất cả provider tự động đều lỗi.
"""

import logging
import json
from datetime import datetime, timezone
from typing import List

from services.providers.base import (
    BaseRateProvider,
    BaseGoldProvider,
    RateData,
    GoldData,
    ProviderResult,
)

logger = logging.getLogger(__name__)


class ManualRateProvider(BaseRateProvider):
    """Provider tỷ giá nhập tay."""

    def __init__(self, manual_rates: dict = None):
        self._rates = manual_rates or {}

    @property
    def name(self) -> str:
        return "manual"

    def set_rates(self, rates: dict) -> None:
        """rates: {"USD": {"buy": 24500, "sell": 24900, "transfer": 24800}, ...}"""
        self._rates = rates

    def fetch_rates(self) -> ProviderResult:
        if not self._rates:
            return ProviderResult(success=False, source="manual", message="Chưa có tỷ giá nhập tay")

        data: List[RateData] = []
        for code, vals in self._rates.items():
            data.append(
                RateData(
                    currency_code=code,
                    currency_name=code,
                    buy_rate=float(vals.get("buy", 0)),
                    sell_rate=float(vals.get("sell", 0)),
                    transfer_rate=float(vals.get("transfer", 0)),
                )
            )

        return ProviderResult(
            success=True,
            data=data,
            source="manual",
            message=f"Tỷ giá nhập tay: {len(data)} loại",
            fetched_at=datetime.now(timezone.utc),
        )


class ManualGoldProvider(BaseGoldProvider):
    """Provider giá vàng nhập tay."""

    def __init__(self, manual_prices: dict = None):
        self._prices = manual_prices or {}

    @property
    def name(self) -> str:
        return "manual"

    def set_prices(self, prices: dict) -> None:
        """prices: {"SJC 1L": {"buy": 87500000, "sell": 89500000}, ...}"""
        self._prices = prices

    def fetch_prices(self) -> ProviderResult:
        if not self._prices:
            return ProviderResult(success=False, source="manual", message="Chưa có giá vàng nhập tay")

        data: List[GoldData] = []
        for gold_type, vals in self._prices.items():
            data.append(
                GoldData(
                    gold_type=gold_type,
                    buy_price=float(vals.get("buy", 0)),
                    sell_price=float(vals.get("sell", 0)),
                    unit="lượng",
                )
            )

        return ProviderResult(
            success=True,
            data=data,
            source="manual",
            message=f"Giá vàng nhập tay: {len(data)} loại",
            fetched_at=datetime.now(timezone.utc),
        )
