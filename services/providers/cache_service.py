"""Cache service - In-memory + DB cache cho tỷ giá và giá vàng."""

import logging
import time
import threading
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from services.providers.base import RateData, GoldData

logger = logging.getLogger(__name__)


class CacheEntry:
    """Một mục cache."""

    def __init__(self, data: Any, ttl: int):
        self.data = data
        self.created_at = time.time()
        self.ttl = ttl

    @property
    def is_valid(self) -> bool:
        return (time.time() - self.created_at) < self.ttl


class CacheService:
    """In-memory cache service, thread-safe."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._cache: Dict[str, CacheEntry] = {}
        return cls._instance

    def get(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        if entry and entry.is_valid:
            return entry.data
        return None

    def set(self, key: str, data: Any, ttl: int = 1800) -> None:
        self._cache[key] = CacheEntry(data, ttl)

    def invalidate(self, key: str) -> None:
        self._cache.pop(key, None)

    def clear(self) -> None:
        self._cache.clear()

    def get_age(self, key: str) -> Optional[float]:
        """Tuổi cache tính bằng giây."""
        entry = self._cache.get(key)
        if entry:
            return time.time() - entry.created_at
        return None

    def get_created_at(self, key: str) -> Optional[datetime]:
        entry = self._cache.get(key)
        if entry:
            return datetime.fromtimestamp(entry.created_at, tz=timezone.utc)
        return None


# Singleton
cache_service = CacheService()
