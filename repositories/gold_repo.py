"""Gold repository."""

from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.gold import GoldPrice, GoldHolding
from repositories.base import BaseRepository


class GoldPriceRepository(BaseRepository[GoldPrice]):
    def __init__(self, session: Session):
        super().__init__(GoldPrice, session)

    def get_latest(self) -> List[GoldPrice]:
        subq = (
            self.session.query(
                GoldPrice.gold_type,
                func.max(GoldPrice.fetched_at).label("max_fetched"),
            )
            .group_by(GoldPrice.gold_type)
            .subquery()
        )
        return (
            self.session.query(GoldPrice)
            .join(
                subq,
                (GoldPrice.gold_type == subq.c.gold_type)
                & (GoldPrice.fetched_at == subq.c.max_fetched),
            )
            .order_by(GoldPrice.gold_type)
            .all()
        )

    def get_latest_by_type(self, gold_type: str) -> Optional[GoldPrice]:
        return (
            self.session.query(GoldPrice)
            .filter(GoldPrice.gold_type == gold_type)
            .order_by(GoldPrice.fetched_at.desc())
            .first()
        )

    def bulk_insert(self, prices: List[GoldPrice]) -> None:
        self.session.add_all(prices)
        self.session.flush()

    def get_cached_within(self, seconds: int) -> List[GoldPrice]:
        cutoff = datetime.utcnow() - timedelta(seconds=seconds)
        subq = (
            self.session.query(
                GoldPrice.gold_type,
                func.max(GoldPrice.fetched_at).label("max_fetched"),
            )
            .filter(GoldPrice.fetched_at >= cutoff)
            .group_by(GoldPrice.gold_type)
            .subquery()
        )
        return (
            self.session.query(GoldPrice)
            .join(
                subq,
                (GoldPrice.gold_type == subq.c.gold_type)
                & (GoldPrice.fetched_at == subq.c.max_fetched),
            )
            .all()
        )


class GoldHoldingRepository(BaseRepository[GoldHolding]):
    def __init__(self, session: Session):
        super().__init__(GoldHolding, session)

    def get_by_user(self, user_id: int) -> List[GoldHolding]:
        return (
            self.session.query(GoldHolding)
            .filter(GoldHolding.user_id == user_id, GoldHolding.is_deleted == 0)
            .order_by(GoldHolding.buy_date.desc())
            .all()
        )
