import asyncio
import threading
from typing import List, Dict
from uuid import UUID
from decimal import Decimal
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel

from order_book_simulator.config import OrderRequest, Trade
from order_book_simulator.config.order_request import Side
from order_book_simulator.core import OrderBook, MatchingEngine, TraderAccountManager
from order_book_simulator.websocket import ConnectionManager
from order_book_simulator.analysis.metrics import MetricsCalculator


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
        self.metrics_calculator = MetricsCalculator(self.order_book, tick_size=0.01)
        self.matching_engine = MatchingEngine(
            self.order_book,
            self.connection_manager,
            asyncio.get_event_loop(),
            self.metrics_calculator,
        )
        self.account_manager = TraderAccountManager()
        self.lock = threading.Lock()


app_state = AppState()


# dependable function to get app state
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
    with state.lock:
        # Try to get the trader first
        trader = state.account_manager.get_trader_by_username(trader_request.username)
        if trader:
            # If trader exists, return their account details
            account = state.account_manager.get_account(trader.trader_id)
        else:
            # If trader does not exist, create a new one
            try:
                trader_id = state.account_manager.register_trader(
                    trader_request.username
                )
                account = state.account_manager.get_account(trader_id)
            except ValueError as e:
                # This might happen in a race condition, though the lock should prevent it.
                raise HTTPException(status_code=400, detail=str(e))

        return AccountResponse(
            trader_id=account.trader_id,
            username=account.username,
            balance=account.balance,
            active=account.active,
        )


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


@router.get("/traders", response_model=List[AccountResponse], tags=["Traders"])
def get_all_traders(state: AppState = Depends(get_app_state)) -> List[AccountResponse]:
    """Get all trader accounts.

    Args:
        state (AppState): Application state

    Returns:
        List[AccountResponse]: A list of all trader accounts
    """
    from order_book_simulator.database.session import get_db
    from order_book_simulator.database.models import DBTraderAccount

    with get_db() as db:
        accounts = db.query(DBTraderAccount).all()
        return [
            AccountResponse(
                trader_id=acc.trader_id,
                username=acc.username,
                balance=acc.balance,
                active=acc.active,
            )
            for acc in accounts
        ]


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
    if order_request.side == Side.BUY:
        required_funds = Decimal(str(order_request.price * order_request.quantity))
        if account.balance < required_funds:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient funds. Required: {required_funds}, Available: {account.balance}",
            )

    from order_book_simulator.database.session import get_db
    from order_book_simulator.database.models import DBOrder, DBTrade

    with state.lock:
        # Create and store the order in database
        with get_db() as db:
            db_order = DBOrder(
                order_id=str(order_request.order_id),
                trader_id=str(order_request.trader_id),
                side=order_request.side.value.lower(),
                price=Decimal(str(order_request.price)),
                quantity=Decimal(str(order_request.quantity)),
                remaining_quantity=Decimal(str(order_request.quantity)),
                priority=order_request.priority,
                status="ACTIVE",
            )
            db.add(db_order)
            db.commit()

        # Process the order and get executed trades
        executed_trades = state.matching_engine.process_order(order_request)

        # Update database with trades and update order status
        with get_db() as db:
            for trade in executed_trades:
                trade_value = Decimal(str(trade.price * trade.quantity))

                # Record the trade
                db_trade = DBTrade(
                    trader_id=str(trade.taker_trader_id),
                    order_id=str(trade.taker_order_id),
                    side=trade.taker_side.value,
                    price=Decimal(str(trade.price)),
                    quantity=Decimal(str(trade.quantity)),
                    counter_party_id=str(trade.maker_trader_id),
                )
                db.add(db_trade)

                # Update order's remaining quantity and status
                order = (
                    db.query(DBOrder)
                    .filter(DBOrder.order_id == str(trade.taker_order_id))
                    .first()
                )
                if order:
                    order.remaining_quantity -= Decimal(str(trade.quantity))
                    if order.remaining_quantity <= 0:
                        order.status = "FILLED"

                # Update maker order's remaining quantity and status
                maker_order = (
                    db.query(DBOrder)
                    .filter(DBOrder.order_id == str(trade.maker_order_id))
                    .first()
                )
                if maker_order:
                    maker_order.remaining_quantity -= Decimal(str(trade.quantity))
                    if maker_order.remaining_quantity <= 0:
                        maker_order.status = "FILLED"

                # The taker is the one who initiated the order
                taker_id = trade.taker_trader_id
                maker_id = trade.maker_trader_id

                # If the taker is buying, they spend money and the maker receives it
                if trade.taker_side == Side.BUY:
                    state.account_manager.update_balance(taker_id, -trade_value)
                    state.account_manager.update_balance(maker_id, trade_value)
                # If the taker is selling, they receive money and the maker spends it
                else:  # Taker side is "sell"
                    state.account_manager.update_balance(taker_id, trade_value)
                    state.account_manager.update_balance(maker_id, -trade_value)

            db.commit()

    return executed_trades


@router.get("/trades", tags=["Trades"])
def get_all_trades(state: AppState = Depends(get_app_state)) -> List[dict]:
    """Get all trades from the database.

    Args:
        state (AppState): Application state

    Returns:
        List[dict]: List of all trades
    """
    from order_book_simulator.database.session import get_db
    from order_book_simulator.database.models import DBTrade

    with get_db() as db:
        trades = db.query(DBTrade).all()
        return [
            {
                "trade_id": trade.trade_id,
                "trader_id": trade.trader_id,
                "order_id": trade.order_id,
                "side": trade.side,
                "price": float(trade.price),
                "quantity": float(trade.quantity),
                "timestamp": trade.timestamp.timestamp(),
            }
            for trade in trades
        ]


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


@router.get("/orders", tags=["Orders"])
def get_all_orders(state: AppState = Depends(get_app_state)) -> List[dict]:
    """Get all orders from the database.

    Args:
        state (AppState): Application state

    Returns:
        List[dict]: List of all orders
    """
    from order_book_simulator.database.session import get_db
    from order_book_simulator.database.models import DBOrder

    with get_db() as db:
        orders = db.query(DBOrder).all()
        return [
            {
                "order_id": order.order_id,
                "trader_id": order.trader_id,
                "side": order.side,
                "price": float(order.price),
                "quantity": float(order.quantity),
                "remaining_quantity": float(order.remaining_quantity),
                "status": order.status,
                "timestamp": order.timestamp.timestamp(),
            }
            for order in orders
        ]


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
