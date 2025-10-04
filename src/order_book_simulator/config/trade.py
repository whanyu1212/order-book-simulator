import time
from datetime import datetime, timezone
from .order_request import Side
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class Trade(BaseModel):

    trade_id: UUID = Field(
        default_factory=uuid4,
        description="The unique identifier for this specific trade event.",
    )

    maker_order_id: UUID = Field(
        description="The ID of the order that was resting on the book (providing liquidity)."
    )
    taker_order_id: UUID = Field(
        description="The ID of the incoming order that executed against the maker (taking liquidity)."
    )

    price: float = Field(
        description="The price at which the trade was executed. This is always the price of the maker order."
    )
    quantity: int = Field(description="The quantity of the asset that was traded.")

    taker_side: Side = Field(
        description="The side (buy/sell) of the TAKER order. This determines the direction of the trade."
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="The timezone-aware timestamp of when the trade occurred.",
    )
