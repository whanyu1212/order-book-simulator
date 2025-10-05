from fastapi import FastAPI

from order_book_simulator.api import router as api_router


app = FastAPI(
    title="Order Book Simulator API",
    description="An API for a live limit order book matching engine.",
)

app.include_router(api_router)
