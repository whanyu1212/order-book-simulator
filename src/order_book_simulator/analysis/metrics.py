import time
import numpy as np
from rich import print
from rich.console import Console
from order_book_simulator.config.order_request import OrderRequest
from order_book_simulator.core import OrderBook

console = Console()


class MetricsCalculator:
    def __init__(self, order_book: OrderBook, tick_size: float):
        self.order_book = order_book
        self.tick_size = tick_size
        self.timestamps = []
        self.spread_ticks = []
        self.spread_bps = []
        self.depth_dollars = []

    def take_snapshot(self, timestamp: float) -> None:
        """a snapshot of the current order book state
        and the metrics at that moment

        Args:
            timestamp (float): timestamp in unix

        """
        best_bid = self.order_book.best_bid
        best_ask = self.order_book.best_ask

        # some runtime error handling
        if best_bid is None or best_ask is None:
            return

        # --- A. Bid-Ask Spread Calculation ---
        spread_dollars = best_ask - best_bid
        spread_ticks = spread_dollars / self.tick_size

        midpoint = (best_ask + best_bid) / 2
        spread_bps = (spread_dollars / midpoint) * 10000

        # --- B. Market Depth Calculation ---
        bid_volume = self.order_book.get_best_bid_volume()
        ask_volume = self.order_book.get_best_ask_volume()

        dollar_bid_depth = best_bid * bid_volume
        dollar_ask_depth = best_ask * ask_volume
        total_dollar_depth = dollar_bid_depth + dollar_ask_depth

        self.timestamps.append(timestamp)
        self.spread_ticks.append(spread_ticks)
        self.spread_bps.append(spread_bps)
        self.depth_dollars.append(total_dollar_depth)

    def calculate_averages(self) -> dict:
        """Calculate the final metrics after the last
        order event

        Returns:
            dict: a dict containing summary metrics
        """
        if not self.timestamps:
            console.print(
                "No valid snapshots were taken to calculate averages.", style="yellow"
            )
            return

        # Convert lists to NumPy arrays for slight performance boost
        spread_ticks_arr = np.array(self.spread_ticks)
        spread_bps_arr = np.array(self.spread_bps)
        depth_dollars_arr = np.array(self.depth_dollars)

        avg_spread_ticks = np.mean(spread_ticks_arr)
        avg_spread_bps = np.mean(spread_bps_arr)
        avg_depth_dollars = np.mean(depth_dollars_arr)

        console.print("--- Final Metrics ---", style="bold blue")
        console.print(
            f"Average Bid-Ask Spread (in Ticks): [bold green]{avg_spread_ticks:.4f}[/bold green]"
        )
        console.print(
            f"Average Bid-Ask Spread (in Basis Points): [bold green]{avg_spread_bps:.4f}[/bold green]"
        )
        console.print(
            f"Average Best-Level Market Depth (in Dollars): [bold green]${avg_depth_dollars:,.2f}[/bold green]"
        )

        return {
            "avg_spread_ticks": avg_spread_ticks,
            "avg_spread_bps": avg_spread_bps,
            "avg_depth_dollars": avg_depth_dollars,
        }
