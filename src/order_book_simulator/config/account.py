from dataclasses import dataclass, field
from uuid import UUID
from decimal import Decimal
from typing import Any


# Since it is internal data structure and we are not receiving this piece of data
# from external sources, we can use dataclass for simplicity. It is more lightweight
# than pydantic BaseModel and does not require validation overhead.
@dataclass
class TraderAccount:
    """Represents a trader's account with their balance and status"""

    trader_id: UUID = field(
        metadata={"description": "Unique identifier for the trader"}
    )
    username: str = field(metadata={"description": "Unique username for the trader"})
    balance: Decimal = field(
        metadata={"description": "Current balance in the trader's account"}
    )
    active: bool = field(
        default=True,
        metadata={"description": "Whether the trader account is active or disabled"},
    )


if __name__ == "__main__":
    from uuid import uuid4
    from rich import print  # slightly nicer output

    trader = TraderAccount(
        trader_id=uuid4(), username="trader1", balance=Decimal("1000.00")
    )
    print(trader)
