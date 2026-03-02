"""Stock repository - CRUD chứng khoán."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.stock import StockHolding
from repositories.base import BaseRepository


class StockHoldingRepository(BaseRepository[StockHolding]):
    def __init__(self, session: Session):
        super().__init__(StockHolding, session)

    def get_by_user(self, user_id: int) -> List[StockHolding]:
        return (
            self.session.query(StockHolding)
            .filter(StockHolding.user_id == user_id, StockHolding.is_deleted == 0)
            .order_by(StockHolding.ticker, StockHolding.buy_date.desc())
            .all()
        )

    def get_by_ticker(self, user_id: int, ticker: str) -> List[StockHolding]:
        return (
            self.session.query(StockHolding)
            .filter(
                StockHolding.user_id == user_id,
                StockHolding.ticker == ticker.upper(),
                StockHolding.is_deleted == 0,
            )
            .all()
        )

    def get_portfolio_summary(self, user_id: int) -> List[dict]:
        """Tổng hợp danh mục theo mã.

        Trả về list dict: ticker, name, exchange, total_qty, avg_price,
        current_price, market_value, cost, profit, profit_pct
        """
        holdings = self.get_by_user(user_id)
        ticker_map: dict[str, dict] = {}
        for h in holdings:
            key = h.ticker.upper()
            if key not in ticker_map:
                ticker_map[key] = {
                    "ticker": key,
                    "name": h.name or key,
                    "exchange": h.exchange or "",
                    "total_qty": 0,
                    "total_cost": 0.0,
                    "current_price": h.current_price or 0,
                }
            bucket = ticker_map[key]
            bucket["total_qty"] += h.quantity
            bucket["total_cost"] += h.quantity * h.avg_price
            # Sử dụng giá mới nhất nếu có
            if h.current_price and h.current_price > 0:
                bucket["current_price"] = h.current_price

        result = []
        for t in ticker_map.values():
            qty = t["total_qty"]
            cost = t["total_cost"]
            avg = cost / qty if qty else 0
            mv = qty * t["current_price"]
            profit = mv - cost
            pct = (profit / cost * 100) if cost else 0
            result.append({
                "ticker": t["ticker"],
                "name": t["name"],
                "exchange": t["exchange"],
                "total_qty": qty,
                "avg_price": avg,
                "current_price": t["current_price"],
                "market_value": mv,
                "cost": cost,
                "profit": profit,
                "profit_pct": pct,
            })
        return sorted(result, key=lambda x: x["market_value"], reverse=True)
