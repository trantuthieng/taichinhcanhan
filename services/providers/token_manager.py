"""Token Manager - Quản lý API token VNAppMob.

Tự động request, cache, refresh token theo scope.
Xử lý 403 bằng cách request key mới và retry.
"""

import logging
import time
import threading
from typing import Optional, Dict
from datetime import datetime, timezone
import requests

from config import settings

logger = logging.getLogger(__name__)


class TokenInfo:
    """Thông tin token."""

    def __init__(self, token: str, scope: str, ttl: int):
        self.token = token
        self.scope = scope
        self.issued_at = time.time()
        self.ttl = ttl
        self.expires_at = self.issued_at + ttl

    @property
    def is_expired(self) -> bool:
        return time.time() >= self.expires_at

    @property
    def should_refresh(self) -> bool:
        """Refresh nếu còn ít hơn 10% thời gian sống."""
        remaining = self.expires_at - time.time()
        return remaining < (self.ttl * 0.1)


class TokenManager:
    """Quản lý API tokens cho VNAppMob.

    - Request token theo scope (gold, exchange_rate)
    - Lưu issued_at / expires_at
    - Refresh trước hạn
    - Refresh khi gặp 403
    - Thread-safe
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._tokens: Dict[str, TokenInfo] = {}
                    cls._instance._base_url = settings.VNAPPMOB_BASE_URL
                    cls._instance._ttl = settings.TOKEN_TTL
        return cls._instance

    def get_token(self, scope: str) -> Optional[str]:
        """Lấy token hợp lệ cho scope. Request mới nếu cần."""
        token_info = self._tokens.get(scope)

        if token_info and not token_info.should_refresh:
            return token_info.token

        # Token hết hạn hoặc sắp hết -> request mới
        new_token = self._request_new_token(scope)
        if new_token:
            return new_token

        # Nếu request mới thất bại, dùng token cũ nếu chưa expired hoàn toàn
        if token_info and not token_info.is_expired:
            return token_info.token

        return None

    def force_refresh(self, scope: str) -> Optional[str]:
        """Buộc refresh token (gọi khi gặp 403)."""
        logger.info(f"Force refresh token cho scope: {scope}")
        return self._request_new_token(scope)

    def _request_new_token(self, scope: str) -> Optional[str]:
        """Gọi API để lấy token mới."""
        url = f"{self._base_url}/request_api_key"
        params = {"scope": scope}

        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                token = data.get("results", "")
                if token:
                    self._tokens[scope] = TokenInfo(token, scope, self._ttl)
                    logger.info(f"Token mới cho scope '{scope}' đã được cấp.")
                    return token
                else:
                    logger.warning(f"API trả về results rỗng cho scope '{scope}'.")
            else:
                logger.warning(f"Request token thất bại: HTTP {resp.status_code}")
        except requests.RequestException as e:
            logger.error(f"Lỗi kết nối khi request token: {e}")

        return None

    def get_token_status(self, scope: str) -> dict:
        """Trả về thông tin trạng thái token."""
        info = self._tokens.get(scope)
        if not info:
            return {"status": "no_token", "scope": scope}

        now = time.time()
        return {
            "scope": scope,
            "status": "expired" if info.is_expired else ("refreshing" if info.should_refresh else "active"),
            "issued_at": datetime.fromtimestamp(info.issued_at, tz=timezone.utc).isoformat(),
            "expires_at": datetime.fromtimestamp(info.expires_at, tz=timezone.utc).isoformat(),
            "remaining_seconds": max(0, int(info.expires_at - now)),
        }

    def invalidate(self, scope: str) -> None:
        """Xóa token khỏi cache."""
        self._tokens.pop(scope, None)


# Singleton instance
token_manager = TokenManager()
