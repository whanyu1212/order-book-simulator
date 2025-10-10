from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple
from sqlalchemy import desc
from sqlalchemy.orm import Session

from order_book_simulator.database import DBTrade, DBTraderAccount, get_db


class TradeHistoryTracker:
    """Tracks and analyzes trade history"""

    @staticmethod
    def record_trade(
        trade_id: str,
        trader_id: str,
        order_id: str,
        side: str,
        price: Decimal,
        quantity: Decimal,
        counter_party_id: Optional[str] = None,
        fee: Decimal = Decimal("0"),
    ) -> None:
        """Record a new trade"""
        with get_db() as db:
            trade = DBTrade(
                trade_id=trade_id,
                trader_id=trader_id,
                order_id=order_id,
                side=side,
                price=price,
                quantity=quantity,
                counter_party_id=counter_party_id,
                fee=fee,
            )
            db.add(trade)
            db.commit()

    @staticmethod
    def get_trader_history(trader_id: str, limit: int = 100) -> List[DBTrade]:
        """Get trader's trade history"""
        with get_db() as db:
            return (
                db.query(DBTrade)
                .filter(DBTrade.trader_id == trader_id)
                .order_by(desc(DBTrade.timestamp))
                .limit(limit)
                .all()
            )

    @staticmethod
    def get_trader_stats(trader_id: str) -> dict:
        """Get trader's trading statistics"""
        with get_db() as db:
            # Get all trades for the trader
            trades = db.query(DBTrade).filter(DBTrade.trader_id == trader_id).all()

            total_volume = Decimal("0")
            buy_volume = Decimal("0")
            sell_volume = Decimal("0")
            total_fees = Decimal("0")
            num_trades = len(trades)

            for trade in trades:
                volume = trade.price * trade.quantity
                total_volume += volume
                if trade.side == "BUY":
                    buy_volume += volume
                else:
                    sell_volume += volume
                total_fees += trade.fee

            return {
                "total_trades": num_trades,
                "total_volume": float(total_volume),
                "buy_volume": float(buy_volume),
                "sell_volume": float(sell_volume),
                "total_fees": float(total_fees),
                "average_trade_size": (
                    float(total_volume / num_trades) if num_trades > 0 else 0
                ),
            }

    @staticmethod
    def get_market_stats(start_time: datetime, end_time: datetime) -> dict:
        """Get market-wide statistics for a time period"""
        with get_db() as db:
            trades = (
                db.query(DBTrade)
                .filter(DBTrade.timestamp.between(start_time, end_time))
                .all()
            )

            total_volume = Decimal("0")
            num_trades = len(trades)
            prices = []

            for trade in trades:
                volume = trade.price * trade.quantity
                total_volume += volume
                prices.append(float(trade.price))

            avg_price = sum(prices) / len(prices) if prices else 0
            high_price = max(prices) if prices else 0
            low_price = min(prices) if prices else 0

            return {
                "period_start": start_time,
                "period_end": end_time,
                "total_trades": num_trades,
                "total_volume": float(total_volume),
                "average_price": avg_price,
                "high_price": high_price,
                "low_price": low_price,
            }

    @staticmethod
    def get_top_traders(
        metric: str = "volume", limit: int = 10
    ) -> List[Tuple[str, float]]:
        """Get top traders by various metrics"""
        with get_db() as db:
            if metric == "volume":
                # Get traders by total trading volume
                results = (
                    db.query(
                        DBTraderAccount.username,
                        db.func.sum(DBTrade.price * DBTrade.quantity).label("volume"),
                    )
                    .join(DBTrade)
                    .group_by(DBTraderAccount.username)
                    .order_by(desc("volume"))
                    .limit(limit)
                    .all()
                )
                return [(r[0], float(r[1])) for r in results]

            elif metric == "trades":
                # Get traders by number of trades
                results = (
                    db.query(
                        DBTraderAccount.username,
                        db.func.count(DBTrade.trade_id).label("num_trades"),
                    )
                    .join(DBTrade)
                    .group_by(DBTraderAccount.username)
                    .order_by(desc("num_trades"))
                    .limit(limit)
                    .all()
                )
                return results
