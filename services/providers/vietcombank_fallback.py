"""Vietcombank XML Fallback Provider.

Fallback cho tỷ giá khi VNAppMob không khả dụng.
Parse XML từ portal Vietcombank.
"""

import logging
import time
from datetime import datetime, timezone
from typing import List
import requests
from xml.etree import ElementTree

from config import settings
from services.providers.base import BaseRateProvider, RateData, ProviderResult

logger = logging.getLogger(__name__)


class VietcombankXmlFallbackProvider(BaseRateProvider):
    """Fallback provider: tỷ giá từ Vietcombank XML."""

    @property
    def name(self) -> str:
        return "vietcombank"

    def fetch_rates(self) -> ProviderResult:
        url = settings.VCB_EXCHANGE_URL

        try:
            start = time.time()
            resp = requests.get(url, timeout=15)
            elapsed = (time.time() - start) * 1000

            if resp.status_code != 200:
                return ProviderResult(
                    success=False, source="fallback", message=f"VCB HTTP {resp.status_code}"
                )

            return self._parse_xml(resp.content, elapsed)

        except requests.Timeout:
            return ProviderResult(success=False, source="fallback", message="VCB timeout")
        except requests.RequestException as e:
            return ProviderResult(success=False, source="fallback", message=str(e))

    def _parse_xml(self, content: bytes, elapsed_ms: float) -> ProviderResult:
        try:
            root = ElementTree.fromstring(content)
        except ElementTree.ParseError as e:
            return ProviderResult(success=False, source="fallback", message=f"XML parse error: {e}")

        rates: List[RateData] = []
        for exrate in root.findall(".//Exrate"):
            try:
                code = exrate.get("CurrencyCode", "")
                name = exrate.get("CurrencyName", "")
                buy = self._parse_vcb_float(exrate.get("Buy", "0"))
                transfer = self._parse_vcb_float(exrate.get("Transfer", "0"))
                sell = self._parse_vcb_float(exrate.get("Sell", "0"))

                if code:
                    rates.append(
                        RateData(
                            currency_code=code,
                            currency_name=name,
                            buy_rate=buy,
                            sell_rate=sell,
                            transfer_rate=transfer,
                        )
                    )
            except (ValueError, KeyError) as e:
                logger.warning(f"Bỏ qua VCB rate lỗi: {e}")

        return ProviderResult(
            success=True,
            data=rates,
            source="fallback",
            message=f"VCB: {len(rates)} tỷ giá trong {elapsed_ms:.0f}ms",
            fetched_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def _parse_vcb_float(val: str) -> float:
        if not val or val == "-":
            return 0.0
        val = val.replace(",", "").strip()
        return float(val) if val else 0.0
