"""Base provider interfaces."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RateData:
    """Dữ liệu tỷ giá."""
    currency_code: str
    currency_name: str = ""
    buy_rate: float = 0.0
    sell_rate: float = 0.0
    transfer_rate: float = 0.0


@dataclass
class GoldData:
    """Dữ liệu giá vàng."""
    gold_type: str
    buy_price: float = 0.0
    sell_price: float = 0.0
    unit: str = "lượng"


@dataclass
class ProviderResult:
    """Kết quả từ provider."""
    success: bool
    data: List[Any] = field(default_factory=list)
    source: str = ""  # realtime, refreshed_token, cached, fallback, manual
    message: str = ""
    fetched_at: Optional[datetime] = None


class BaseRateProvider(ABC):
    """Interface cho provider tỷ giá."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def fetch_rates(self) -> ProviderResult:
        """Lấy tỷ giá ngoại tệ."""
        pass


class BaseGoldProvider(ABC):
    """Interface cho provider giá vàng."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def fetch_prices(self) -> ProviderResult:
        """Lấy giá vàng."""
        pass
