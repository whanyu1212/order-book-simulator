import asyncio
import threading
from typing import List, Dict
from uuid import UUID
from decimal import Decimal
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel

from order_book_simulator.config import OrderRequest, Trade
from order_book_simulator.core import OrderBook, MatchingEngine, TraderAccountManager
from order_book_simulator.websocket import ConnectionManager


# ! sorted dict is not a standard data type that can be
# ! directly converted into JSON for web apis


# We define a few more response sechma just to ensure that
# whatever orderbook returns is JSON serializable
class OrderBookLevel(BaseModel):
    price: float
    quantity: int


class OrderBookResponse(BaseModel):
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]


class TraderRequest(BaseModel):
    username: str


class AccountResponse(BaseModel):
    trader_id: UUID
    username: str
    balance: Decimal
    active: bool


# Application state
class AppState:
    def __init__(self):
        self.order_book = OrderBook()
        self.connection_manager = ConnectionManager()
        self.matching_engine = MatchingEngine(
            self.order_book, self.connection_manager, asyncio.get_event_loop()
        )
        self.account_manager = TraderAccountManager()
        self.lock = threading.Lock()


app_state = AppState()


def get_app_state():
    return app_state


router = APIRouter()

# === Endpoints === #


@router.post("/traders", response_model=AccountResponse, tags=["Traders"])
def create_trader(
    trader_request: TraderRequest, state: AppState = Depends(get_app_state)
) -> AccountResponse:
    """Register a new trader with initial balance.

    Args:
        trader_request (TraderRequest): Registration request with username
        state (AppState): Application state

    Returns:
        AccountResponse: New trader account details

    Raises:
        HTTPException: If username already exists
    """
    try:
        with state.lock:
            trader_id = state.account_manager.register_trader(trader_request.username)
            account = state.account_manager.get_account(trader_id)
            return AccountResponse(
                trader_id=account.trader_id,
                username=account.username,
                balance=account.balance,
                active=account.active,
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/traders/{trader_id}", response_model=AccountResponse, tags=["Traders"])
def get_trader_account(
    trader_id: UUID, state: AppState = Depends(get_app_state)
) -> AccountResponse:
    """Get trader account details.

    Args:
        trader_id (UUID): Trader's unique identifier
        state (AppState): Application state

    Returns:
        AccountResponse: Trader account details

    Raises:
        HTTPException: If trader not found
    """
    account = state.account_manager.get_account(trader_id)
    if not account:
        raise HTTPException(status_code=404, detail="Trader not found")
    return AccountResponse(
        trader_id=account.trader_id,
        username=account.username,
        balance=account.balance,
        active=account.active,
    )


@router.post("/orders", response_model=List[Trade], tags=["Orders"])
def submit_order(
    order_request: OrderRequest, state: AppState = Depends(get_app_state)
) -> List[Trade]:
    """Submit a limit order to the end point

    Args:
        order_request (OrderRequest): order that adheres to the OrderRequest schema
        state (AppState, optional): Defaults to Depends(get_app_state).

    Raises:
        HTTPException: If trader not found or insufficient funds

    Returns:
        List[Trade]: list of trades
    """
    # Check if trader exists and has sufficient funds
    account = state.account_manager.get_account(order_request.trader_id)
    if not account:
        raise HTTPException(
            status_code=404, detail="Trader not found. Please register first."
        )

    if not account.active:
        raise HTTPException(status_code=400, detail="Account is deactivated")

    # For sell orders, check if trader has sufficient assets (to be implemented)
    # For buy orders, check if trader has sufficient funds
    if order_request.side == "BUY":
        required_funds = Decimal(str(order_request.price * order_request.quantity))
        if account.balance < required_funds:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient funds. Required: {required_funds}, Available: {account.balance}",
            )

    with state.lock:
        # Process the order and get executed trades
        executed_trades = state.matching_engine.process_order(order_request)

        # Update balances based on executed trades
        for trade in executed_trades:
            if trade.trader_id == order_request.trader_id:
                # If this trader is the buyer, deduct funds
                if order_request.side == "BUY":
                    state.account_manager.update_balance(
                        trade.trader_id, -Decimal(str(trade.price * trade.quantity))
                    )
                # If this trader is the seller, add funds
                else:
                    state.account_manager.update_balance(
                        trade.trader_id, Decimal(str(trade.price * trade.quantity))
                    )

    return executed_trades


@router.get("/orderbook", response_model=OrderBookResponse, tags=["Order Book"])
def get_order_book(state: AppState = Depends(get_app_state)) -> OrderBookResponse:
    """Returns a JSON representation of the current order book state

    Args:
        state (AppState, optional): Defaults to Depends(get_app_state).

    Returns:
        OrderBookResponse: order book response schema
    """
    with state.lock:
        book_state = {
            "bids": [
                {"price": -neg_price, "quantity": sum(o.quantity for o in orders)}
                for neg_price, orders in state.order_book.bids.items()
            ],
            "asks": [
                {"price": price, "quantity": sum(o.quantity for o in orders)}
                for price, orders in state.order_book.asks.items()
            ],
        }
    return OrderBookResponse(**book_state)


@router.websocket("/ws/trades", name="Trade Updates")
async def websocket_endpoint(
    websocket: WebSocket, state: AppState = Depends(get_app_state)
):
    """WebSocket endpoint for receiving trade updates.

    Args:
        websocket (WebSocket): The WebSocket connection.
        state (AppState, optional): The application state. Defaults to Depends(get_app_state).
    """
    await state.connection_manager.connect(websocket)
    try:
        while True:
            # The server will listen for messages from the client, though in a simple broadcast-only
            # scenario, you might not need to process incoming messages.
            await websocket.receive_text()
    except WebSocketDisconnect:
        state.connection_manager.disconnect(websocket)
