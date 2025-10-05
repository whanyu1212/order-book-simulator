from uuid import uuid4
from collections import deque
from sortedcontainers import SortedDict
from order_book_simulator.config import OrderRequest, Side, Priority
from order_book_simulator.core import OrderBook, MatchingEngine
from rich import print
from rich.table import Table
from rich.json import JSON


if __name__ == "__main__":
    # === 1. Setup === #
    order_book = OrderBook()
    matching_engine = MatchingEngine(order_book)

    # === 2. Pre-populate the Order Book with some resting MAKER orders === #
    print("[bold cyan]--- Populating Initial Order Book ---[/bold cyan]")
    trader1 = uuid4()
    trader2 = uuid4()

    # Add some asks (sell orders)
    matching_engine.process_order(
        OrderRequest(
            trader_id=trader1,
            side=Side.SELL,
            price=101.0,
            quantity=100,
            priority=Priority.MEDIUM,
        )
    )
    matching_engine.process_order(
        OrderRequest(
            trader_id=trader2,
            side=Side.SELL,
            price=102.0,
            quantity=50,
            priority=Priority.MEDIUM,
        )
    )

    # Add some bids (buy orders)
    matching_engine.process_order(
        OrderRequest(
            trader_id=trader1,
            side=Side.BUY,
            price=99.0,
            quantity=75,
            priority=Priority.MEDIUM,
        )
    )
    matching_engine.process_order(
        OrderRequest(
            trader_id=trader2,
            side=Side.BUY,
            price=98.0,
            quantity=100,
            priority=Priority.MEDIUM,
        )
    )

    print("\n[bold green]=== Initial State of the Order Book ===[/bold green]")
    print(order_book)

    # === 3. A new TAKER order arrives that will cross the spread ===
    print("\n[bold yellow]=== A new aggressive BUY order arrives ===[/bold yellow]")
    trader3 = uuid4()
    taker_buy_order = OrderRequest(
        trader_id=trader3,
        side=Side.BUY,
        price=101.5,
        quantity=125,
        priority=Priority.MEDIUM,
    )

    print(
        f"Processing Taker Order: BUY {taker_buy_order.quantity} @ {taker_buy_order.price}"
    )

    # === 4. Process the order and see the results ===
    executed_trades = matching_engine.process_order(taker_buy_order)

    print("\n[bold magenta]=== Trades Executed ===[/bold magenta]")
    if not executed_trades:
        print("[yellow]No trades were executed.[/yellow]")
    else:
        for trade in executed_trades:
            print(JSON(trade.model_dump_json()))

    # === 5. Check the final state of the book ===
    print("\n[bold green]=== Final State of the Order Book ===[/bold green]")
    print(order_book)
