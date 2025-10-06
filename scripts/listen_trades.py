import asyncio
import websockets
import json


async def listen_trades():
    """Connects to the trade feed and prints incoming trades."""
    uri = "ws://127.0.0.1:8000/ws/trades"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"--- Listening for trades on {uri} ---")
            while True:
                try:
                    trade_str = await websocket.recv()
                    trade = json.loads(trade_str)
                    print(f"\n--- New Trade ---")
                    print(json.dumps(trade, indent=2))
                    print("-----------------")
                except websockets.ConnectionClosed:
                    print("Connection to the server was closed.")
                    break
    except (
        OSError,
        websockets.exceptions.InvalidURI,
        websockets.exceptions.InvalidHandshake,
    ) as e:
        print(
            f"Error: Could not connect to {uri}. Please ensure the server is running."
        )
        print(f"Details: {e}")


if __name__ == "__main__":
    asyncio.run(listen_trades())
