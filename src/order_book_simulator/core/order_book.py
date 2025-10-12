from collections import deque
from typing import Deque, Optional
from uuid import uuid4
from order_book_simulator.config import OrderRequest, Side
from io import StringIO
from rich.console import Console
from rich.table import Table
from sortedcontainers import SortedDict


class OrderBook:
    """Manages the state of resting limit orders using SortedDict for efficiency."""

    def __init__(self):
        # For bids, prices are keys. We want to get the highest price first,
        # so we'll store prices as negative values in a SortedDict.
        self.bids = SortedDict()
        self.asks = SortedDict()

    def add_order(self, order: OrderRequest) -> None:
        """Add an order into the side that it belongs

        Args:
            order (OrderRequest): an order that is in the
            OrderRequest format
        """
        price = order.price
        if order.side == Side.BUY:
            book_side = self.bids
            # Use negative price for sorting bids from high to low
            price_key = -price
        else:  # Side.SELL
            book_side = self.asks
            price_key = price

        if price_key not in book_side:
            book_side[price_key] = deque()
        book_side[price_key].append(order)

    def remove_order(self, order: OrderRequest) -> None:
        """Remove an order from the respective side

        Args:
            order (OrderRequest): an order that is in the
            OrderRequest format
        """
        price = order.price
        order_id_to_remove = order.order_id

        if order.side == Side.BUY:
            book_side = self.bids
            price_key = -price
        else:  # Side.SELL
            book_side = self.asks
            price_key = price

        if price_key in book_side:
            orders_at_price = book_side[price_key]
            order_to_remove = next(
                (o for o in orders_at_price if o.order_id == order_id_to_remove), None
            )

            if order_to_remove:
                orders_at_price.remove(order_to_remove)
                if not orders_at_price:
                    del book_side[price_key]

    @property
    def best_bid(self) -> Optional[float]:
        """get the best bid price (highest)

        Returns:
            Optional[float]: price in float if
            self.bids is not empty
        """
        if not self.bids:
            return None
        # The best bid is the highest price, which is the last key in the bids SortedDict
        # (since keys are negative prices, the "first" is the smallest negative, i.e., highest price).
        return -self.bids.peekitem(0)[0]

    @property
    def best_ask(self) -> Optional[float]:
        """get the best asking price (lowest)

        Returns:
            Optional[float]: price in float if
            self.asks is not empty
        """
        if not self.asks:
            return None
        # The best ask is the lowest price, which is the first key in the asks SortedDict.
        return self.asks.peekitem(0)[0]

    def get_best_bid_volume(self) -> Optional[int]:
        """Get the total quantity at the best bid price.

        Returns:
            Optional[int]: total quantity at the best bid price
            or None if no bids exist
        """
        if not self.bids:
            return None
        # peekitem(0) gets the first item (highest bid price)
        best_bid_orders = self.bids.peekitem(0)[1]
        return sum(order.quantity for order in best_bid_orders)

    def get_best_ask_volume(self) -> Optional[int]:
        """Get the total quantity at the best ask price.

        Returns:
            Optional[int]: total quantity at the best ask price
            or None if no asks exist
        """
        if not self.asks:
            return None
        # peekitem(0) gets the first item (lowest ask price)
        best_ask_orders = self.asks.peekitem(0)[1]
        return sum(order.quantity for order in best_ask_orders)

    def __str__(self):
        """Provides a string representation of the order book using rich.table.Table."""
        console = Console(file=StringIO())
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Bid Price", style="cyan", justify="right")
        table.add_column("Bid Quantity", style="cyan", justify="right")
        table.add_column("Ask Price", style="magenta", justify="right")
        table.add_column("Ask Quantity", style="magenta", justify="right")

        bids = [
            (-neg_price, sum(o.quantity for o in orders))
            for neg_price, orders in self.bids.items()
        ]
        asks = [
            (price, sum(o.quantity for o in orders))
            for price, orders in self.asks.items()
        ]

        num_bids = len(bids)
        num_asks = len(asks)
        max_rows = max(num_bids, num_asks)

        for i in range(max_rows):
            bid_price, bid_qty = (
                (f"{bids[i][0]:.2f}", str(bids[i][1])) if i < num_bids else ("", "")
            )
            ask_price, ask_qty = (
                (f"{asks[i][0]:.2f}", str(asks[i][1])) if i < num_asks else ("", "")
            )
            table.add_row(bid_price, bid_qty, ask_price, ask_qty)

        console.print(table)
        return console.file.getvalue()


if __name__ == "__main__":
    # Create an order book
    order_book = OrderBook()

    # Create some orders
    buy_order1 = OrderRequest(
        trader_id=uuid4(), side=Side.BUY, priority=1, price=100.0, quantity=10
    )
    buy_order2 = OrderRequest(
        trader_id=uuid4(), side=Side.BUY, priority=1, price=101.0, quantity=5
    )
    buy_order3 = OrderRequest(
        trader_id=uuid4(), side=Side.BUY, priority=1, price=100.0, quantity=2
    )

    sell_order1 = OrderRequest(
        trader_id=uuid4(), side=Side.SELL, priority=1, price=102.0, quantity=8
    )
    sell_order2 = OrderRequest(
        trader_id=uuid4(), side=Side.SELL, priority=1, price=103.0, quantity=12
    )
    sell_order3 = OrderRequest(
        trader_id=uuid4(), side=Side.SELL, priority=1, price=102.0, quantity=4
    )

    # Add orders to the book
    order_book.add_order(buy_order1)
    order_book.add_order(buy_order2)
    order_book.add_order(buy_order3)
    order_book.add_order(sell_order1)
    order_book.add_order(sell_order2)
    order_book.add_order(sell_order3)

    # Print the order book
    print(order_book)

    # Show best bid and ask
    print(f"Best Bid: {order_book.best_bid}")
    print(f"Best Ask: {order_book.best_ask}\n")

    # Remove an order
    print("Removing order:", buy_order1.order_id)
    order_book.remove_order(buy_order1)

    # Print the order book again
    print(order_book)

    # Show best bid and ask after removal
    print(f"Best Bid after removal: {order_book.best_bid}")
    print(f"Best Ask after removal: {order_book.best_ask}")
