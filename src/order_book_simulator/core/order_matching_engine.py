from typing import List
from order_book_simulator.config import OrderRequest, Trade, Priority, Side
from order_book_simulator.core import OrderBook


class MatchingEngine:
    """
    The MatchingEngine class contains the core logic for order matching.
    """

    def __init__(self, order_book: OrderBook):
        self.order_book = order_book

    def process_order(self, order_request: OrderRequest) -> List[Trade]:
        """Process the order depending on its side

        Args:
            order_request (OrderRequest): order request (BUY/SELL)

        Returns:
            List[Trade]: a list of matched trades
        """
        # Convert the incoming request into a full Order object, which will
        # auto-generate an order_id and timestamp.
        taker_order = OrderRequest(**order_request.model_dump())
        trades: List[Trade] = []

        if taker_order.side == Side.BUY:
            trades = self._match_buy_order(taker_order)
        else:  # Side.SELL
            trades = self._match_sell_order(taker_order)

        # If the taker order has any remaining quantity after matching,
        # it is added to the order book.
        if taker_order.quantity > 0:
            self.order_book.add_order(taker_order)

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

            maker_order = orders_at_best_ask[0]  # Oldest order is at the front

            # The quantity that can be filled per maker
            trade_quantity = min(taker_order.quantity, maker_order.quantity)

            trade = Trade(
                maker_order_id=maker_order.order_id,
                taker_order_id=taker_order.order_id,
                price=maker_order.price,
                quantity=trade_quantity,
                taker_side=taker_order.side,
            )
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

            maker_order = orders_at_best_bid[0]  # Oldest order is at the front

            trade_quantity = min(taker_order.quantity, maker_order.quantity)

            trade = Trade(
                maker_order_id=maker_order.order_id,
                taker_order_id=taker_order.order_id,
                price=maker_order.price,
                quantity=trade_quantity,
                taker_side=taker_order.side,
            )
            trades.append(trade)

            taker_order.quantity -= trade_quantity
            maker_order.quantity -= trade_quantity

            if maker_order.quantity == 0:
                self.order_book.remove_order(maker_order)

        return trades
