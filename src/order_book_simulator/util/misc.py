from uuid import UUID
from rich.table import Table
from typing import List, Dict
from order_book_simulator.config.trade import Trade


def create_trade_table(
    trades: List[Trade], uuid_to_group_map: Dict[UUID, int]
) -> Table:
    """Create a nicely formatted rich table to print the
    trade details

    Args:
        trades (List[Trade]): a list of Trade objects
        uuid_to_group_map (Dict[UUID, int]): dictionary mapping of UUID to group number

    Returns:
        Table: rich table
    """
    table = Table(show_header=True, header_style="bold magenta")

    # Define columns
    table.add_column("Trade #", style="cyan", justify="right")
    table.add_column("Quantity", justify="right")
    table.add_column("Price", justify="right")
    table.add_column("Maker Group", style="green")
    table.add_column("Taker Group", style="blue")
    table.add_column("Side", justify="center")

    # Add rows
    for i, trade in enumerate(trades, 1):
        maker_group = uuid_to_group_map.get(trade.maker_trader_id, "Unknown")
        taker_group = uuid_to_group_map.get(trade.taker_trader_id, "Unknown")

        table.add_row(
            str(i),
            str(trade.quantity),
            f"${trade.price:.2f}",
            str(maker_group),
            str(taker_group),
            trade.taker_side.value,
        )

    return table
