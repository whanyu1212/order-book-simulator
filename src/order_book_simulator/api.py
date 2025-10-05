import threading
from typing import List, Dict
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from order_book_simulator.config import OrderRequest, Trade
from order_book_simulator.core import OrderBook, MatchingEngine


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


# Application state
class AppState:
    def __init__(self):
        self.order_book = OrderBook()
        self.matching_engine = MatchingEngine(self.order_book)
        self.traders_db: Dict[str, UUID] = {}
        self.lock = threading.Lock()


app_state = AppState()


def get_app_state():
    return app_state


router = APIRouter()

# === Endpoints === #


@router.post("/traders", response_model=str, tags=["Traders"])
def create_trader(
    trader_request: TraderRequest, state: AppState = Depends(get_app_state)
) -> str:
    """Registers a new trader. If the username already exists, it returns their
    existing ID. Otherwise, it creates a new trader and returns their new ID.

    Args:
        trader_request (TraderRequest): trader request schema
        state (AppState, optional): Defaults to Depends(get_app_state).

    Returns:
        str: trader id in string
    """

    username = trader_request.username
    if username in state.traders_db:
        return str(state.traders_db[username])

    new_trader_id = uuid4()
    state.traders_db[username] = new_trader_id
    print(f"Registered new trader: '{username}' with ID: {new_trader_id}")
    return str(new_trader_id)


@router.post("/orders", response_model=List[Trade], tags=["Orders"])
def submit_order(
    order_request: OrderRequest, state: AppState = Depends(get_app_state)
) -> List[Trade]:
    """Submit a limit order to the end point

    Args:
        order_request (OrderRequest): order that adheres to the OrderRequest schema
        state (AppState, optional): Defaults to Depends(get_app_state).

    Raises:
        HTTPException: error 404

    Returns:
        List[Trade]: list of trades
    """
    if order_request.trader_id not in state.traders_db.values():
        raise HTTPException(
            status_code=404,
            detail="Trader ID not found. Please register first via the /traders endpoint.",
        )

    with state.lock:
        # Pass the request directly; the engine should be responsible for creating the Order object.
        executed_trades = state.matching_engine.process_order(order_request)

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
