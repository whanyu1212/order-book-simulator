import asyncio
from typing import List
from order_book_simulator.core import OrderBook
from order_book_simulator.websocket import ConnectionManager
from order_book_simulator.config import OrderRequest, Trade, Priority, Side


class MatchingEngine:
    """
    The MatchingEngine class contains the core logic for order matching.
    """

    def __init__(
        self,
        order_book: OrderBook,
        connection_manager: ConnectionManager,
        loop: asyncio.AbstractEventLoop,
    ):
        self.order_book = order_book
        self.connection_manager = connection_manager
        self.loop = loop

    def process_order(self, order_request: OrderRequest) -> List[Trade]:
        """Process the order depending on its side

        Args:
            order_request (OrderRequest): order request (BUY/SELL)

        Returns:
            List[Trade]: a list of matched trades
        """
        trades: List[Trade] = []

        if order_request.side == Side.BUY:
            trades = self._match_buy_order(order_request)
        else:  # Side.SELL
            trades = self._match_sell_order(order_request)

        # If the taker order has any remaining quantity after matching,
        # it is added to the order book.
        if order_request.quantity > 0:
            self.order_book.add_order(order_request)

        return trades

    # === Private methods === #
    def _match_buy_order(self, taker_order: OrderRequest) -> List[Trade]:
        """Matching an incoming BUY (bid) order with the resting
        SELL orders (asks)

        Args:
            taker_order (OrderRequest): the order request from the taker

        Returns:
            List[Trade]: A list of successful matched trade(s)
        """
        trades: List[Trade] = []

        while (
            taker_order.quantity > 0
            and self.order_book.best_ask is not None
            and taker_order.price >= self.order_book.best_ask
        ):

            best_ask_price = self.order_book.best_ask

            orders_at_best_ask = self.order_book.asks[best_ask_price]

            # Find the first order from a different trader
            maker_order = None
            for order in orders_at_best_ask:
                if order.trader_id != taker_order.trader_id:
                    maker_order = order
                    break

            # If no suitable maker order is found, stop matching
            if maker_order is None:
                break

            # The quantity that can be filled per maker
            trade_quantity = min(taker_order.quantity, maker_order.quantity)

            trade = Trade(
                maker_order_id=maker_order.order_id,
                maker_trader_id=maker_order.trader_id,
                taker_order_id=taker_order.order_id,
                taker_trader_id=taker_order.trader_id,
                price=maker_order.price,
                quantity=trade_quantity,
                taker_side=taker_order.side,
            )
            self._broadcast_trades(trade)
            trades.append(trade)

            taker_order.quantity -= trade_quantity
            maker_order.quantity -= trade_quantity

            if maker_order.quantity == 0:
                self.order_book.remove_order(maker_order)

        return trades

    def _match_sell_order(self, taker_order: OrderRequest) -> List[Trade]:
        """Matching an incoming SELL (ask)  order with the resting
        BUY order (bids)

        Args:
            taker_order (OrderRequest): the order request from the taker

        Returns:
            List[Trade]: a list of successfully matched trade(s)
        """
        trades: List[Trade] = []

        while (
            taker_order.quantity > 0
            and self.order_book.best_bid is not None
            and taker_order.price <= self.order_book.best_bid
        ):

            best_bid_price = self.order_book.best_bid

            orders_at_best_bid = self.order_book.bids[-best_bid_price]

            # Find the first order from a different trader
            maker_order = None
            for order in orders_at_best_bid:
                if order.trader_id != taker_order.trader_id:
                    maker_order = order
                    break

            # If no suitable maker order is found, stop matching
            if maker_order is None:
                break

            trade_quantity = min(taker_order.quantity, maker_order.quantity)

            trade = Trade(
                maker_order_id=maker_order.order_id,
                maker_trader_id=maker_order.trader_id,
                taker_order_id=taker_order.order_id,
                taker_trader_id=taker_order.trader_id,
                price=maker_order.price,
                quantity=trade_quantity,
                taker_side=taker_order.side,
            )
            self._broadcast_trades(trade)
            trades.append(trade)

            taker_order.quantity -= trade_quantity
            maker_order.quantity -= trade_quantity

            if maker_order.quantity == 0:
                self.order_book.remove_order(maker_order)

        return trades

    def _broadcast_trades(self, trade: Trade) -> None:
        """Broadcasts the list of trades to all connected WebSocket clients.

        Args:
            trade (Trade): The trade information to broadcast.
        """
        asyncio.run_coroutine_threadsafe(
            self.connection_manager.broadcast_trade(trade),
            self.loop,
        )
