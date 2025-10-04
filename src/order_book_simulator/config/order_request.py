from pydantic import BaseModel, Field  # Field is meant for additional configuration
import time
from enum import IntEnum, Enum
from typing import Literal
from uuid import UUID, uuid4  # can use 1, 3, 4, 5
from rich import print


class Side(Enum):
    BUY = "buy"
    SELL = "sell"


# TODO: think about the scenarios where this can be used
class Priority(IntEnum):
    High = 1
    Medium = 2
    Low = 3


# * Remark: The primary benefits of using pydantic basemodel here instead of dataclass
# * is that it has runtime data validation, something like pandera for dataframe, and auto
# * data coercion e.g. "100" for price will be converted to 100
class OrderRequest(BaseModel):

    # Optional, auto generated if not provided

    # Universally Unique Identifier, usually represented by 32-character hexadecimal string
    order_id: UUID = Field(
        default_factory=uuid4,
        description="The unique identifier for this specific order.",
    )
    timestamp: float = Field(
        default_factory=time.time,
        description="The timestamp of when the order is created.",
    )

    # Compulsory, must be provided by the user
    trader_id: UUID = Field(description="The ID of the trader placing the order.")
    side: Side = Field(description="The side of the order (buy or sell).")
    priority: Priority = Field(description="The priority of the order.")
    price: float = Field(gt=0, description="The price of the order.")
    quantity: int = Field(gt=0, description="The quantity of the order.")


if __name__ == "__main__":
    trader_id = uuid4()
    side = Side.BUY
    priority = Priority.High
    price = 100
    quantity = 1
    new_order = OrderRequest(
        trader_id=trader_id,
        side=side,
        priority=priority,
        price=price,
        quantity=quantity,
    )
    print(new_order)
