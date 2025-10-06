import asyncio
from typing import List
from fastapi import WebSocket

from order_book_simulator.config import Trade


class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """Accepts a new WebSocket connection.

        Args:
            websocket (WebSocket): The WebSocket connection to accept.
        """
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """Removes a WebSocket connection.

        Args:
            websocket (WebSocket): The WebSocket connection to remove.
        """
        self.active_connections.remove(websocket)

    async def broadcast_trade(self, trade: Trade) -> None:
        """Broadcasts a new trade to all connected clients.

        Args:
            trade (Trade): The trade information to broadcast.
        """
        # Convert the Pydantic model to a JSON-serializable dictionary
        trade_json = trade.model_dump_json()

        # Create a list of send tasks to run them concurrently
        send_tasks = [
            connection.send_text(trade_json) for connection in self.active_connections
        ]
        # Run all send tasks
        await asyncio.gather(*send_tasks)
