"""FX rate repository."""

from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.fx_rate import FxRate
from repositories.base import BaseRepository


class FxRateRepository(BaseRepository[FxRate]):
    def __init__(self, session: Session):
        super().__init__(FxRate, session)

    def get_latest(self, currency_code: str = None) -> List[FxRate]:
        """Lấy tỷ giá mới nhất (grouped by currency)."""
        subq = (
            self.session.query(
                FxRate.currency_code,
                func.max(FxRate.fetched_at).label("max_fetched"),
            )
            .group_by(FxRate.currency_code)
            .subquery()
        )
        q = self.session.query(FxRate).join(
            subq,
            (FxRate.currency_code == subq.c.currency_code)
            & (FxRate.fetched_at == subq.c.max_fetched),
        )
        if currency_code:
            q = q.filter(FxRate.currency_code == currency_code)
        return q.order_by(FxRate.currency_code).all()

    def get_latest_single(self, currency_code: str) -> Optional[FxRate]:
        return (
            self.session.query(FxRate)
            .filter(FxRate.currency_code == currency_code)
            .order_by(FxRate.fetched_at.desc())
            .first()
        )

    def bulk_insert(self, rates: List[FxRate]) -> None:
        self.session.add_all(rates)
        self.session.flush()

    def get_cached_within(self, seconds: int) -> List[FxRate]:
        """Lấy tỷ giá đã cache trong khoảng thời gian."""
        cutoff = datetime.utcnow() - timedelta(seconds=seconds)
        subq = (
            self.session.query(
                FxRate.currency_code,
                func.max(FxRate.fetched_at).label("max_fetched"),
            )
            .filter(FxRate.fetched_at >= cutoff)
            .group_by(FxRate.currency_code)
            .subquery()
        )
        return (
            self.session.query(FxRate)
            .join(
                subq,
                (FxRate.currency_code == subq.c.currency_code)
                & (FxRate.fetched_at == subq.c.max_fetched),
            )
            .all()
        )
