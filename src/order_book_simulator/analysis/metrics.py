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
        self.imbalance = []

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

        # --- C. Order Imbalance ---
        total_volume = bid_volume + ask_volume
        if total_volume > 0:
            imbalance = (bid_volume - ask_volume) / total_volume
        else:
            imbalance = 0.0

        self.timestamps.append(timestamp)
        self.spread_ticks.append(spread_ticks)
        self.spread_bps.append(spread_bps)
        self.depth_dollars.append(total_dollar_depth)  # average of bid and ask depth
        self.imbalance.append(imbalance)

    def calculate_averages(self, final_timestamp: float) -> dict:
        """Calculate the final metrics after the last
        order event using both simple mean and time-weighted averages

        Args:
            final_timestamp (float): The timestamp of the end of the simulation.

        Returns:
            dict: a dict containing summary metrics
        """
        if not self.timestamps:
            console.print(
                "No valid snapshots were taken to calculate averages.", style="yellow"
            )
            return {}

        # Convert lists to NumPy arrays
        timestamps_arr = np.array(self.timestamps)
        spread_ticks_arr = np.array(self.spread_ticks)
        spread_bps_arr = np.array(self.spread_bps)
        depth_dollars_arr = np.array(self.depth_dollars)
        imbalance_arr = np.array(self.imbalance)

        # Simple mean calculations
        avg_spread_ticks = np.mean(spread_ticks_arr)
        avg_spread_bps = np.mean(spread_bps_arr)
        avg_depth_dollars = np.mean(depth_dollars_arr)
        avg_imbalance = np.mean(imbalance_arr)

        # Time-weighted average calculations
        # Time-weighted average calculations
        # Include the final timestamp to account for the duration of the last snapshot
        all_timestamps = np.append(timestamps_arr, final_timestamp)
        time_diffs = np.diff(all_timestamps)

        if len(time_diffs) > 0 and np.sum(time_diffs) > 0:
            total_time = np.sum(time_diffs)

            tw_avg_spread_ticks = np.sum(spread_ticks_arr * time_diffs) / total_time
            tw_avg_spread_bps = np.sum(spread_bps_arr * time_diffs) / total_time
            tw_avg_depth_dollars = np.sum(depth_dollars_arr * time_diffs) / total_time
            tw_avg_imbalance = np.sum(imbalance_arr * time_diffs) / total_time
        else:
            # Fallback to simple mean if only one snapshot or no time has passed
            tw_avg_spread_ticks = avg_spread_ticks
            tw_avg_spread_bps = avg_spread_bps
            tw_avg_depth_dollars = avg_depth_dollars
            tw_avg_imbalance = avg_imbalance

        console.print("--- Final Metrics ---", style="bold blue")
        console.print("\n[bold cyan]Simple Average (Arithmetic Mean):[/bold cyan]")
        console.print(
            f"  Simple Avg Bid-Ask Spread (in Ticks): [bold green]{avg_spread_ticks:.4f}[/bold green]"
        )
        console.print(
            f"  Simple Avg Bid-Ask Spread (in Basis Points): [bold green]{avg_spread_bps:.4f}[/bold green]"
        )
        console.print(
            f"  Simple Avg Best-Level Market Depth (in Dollars): [bold green]${avg_depth_dollars:,.2f}[/bold green]"
        )
        console.print(
            f"  Simple Avg Order Imbalance: [bold green]{avg_imbalance:+.4f}[/bold green]"
        )

        console.print("\n[bold cyan]Time-Weighted Average:[/bold cyan]")
        console.print(
            f"  Time-Weighted Avg Bid-Ask Spread (in Ticks): [bold green]{tw_avg_spread_ticks:.4f}[/bold green]"
        )
        console.print(
            f"  Time-Weighted Avg Bid-Ask Spread (in Basis Points): [bold green]{tw_avg_spread_bps:.4f}[/bold green]"
        )
        console.print(
            f"  Time-Weighted Avg Best-Level Market Depth (in Dollars): [bold green]${tw_avg_depth_dollars:,.2f}[/bold green]"
        )
        console.print(
            f"  Time-Weighted Avg Order Imbalance: [bold green]{tw_avg_imbalance:+.4f}[/bold green]"
        )

        return {
            "avg_spread_ticks": avg_spread_ticks,
            "avg_spread_bps": avg_spread_bps,
            "avg_depth_dollars": avg_depth_dollars,
            "tw_avg_spread_ticks": tw_avg_spread_ticks,
            "tw_avg_spread_bps": tw_avg_spread_bps,
            "tw_avg_depth_dollars": tw_avg_depth_dollars,
            "avg_imbalance": avg_imbalance,
            "tw_avg_imbalance": tw_avg_imbalance,
        }
