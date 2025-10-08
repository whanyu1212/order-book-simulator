from uuid import UUID, uuid4
from decimal import Decimal
from typing import Dict, Optional
from order_book_simulator.config.account import TraderAccount


class TraderAccountManager:
    """Manages trader accounts, balances, and registration"""

    def __init__(self, initial_balance: Decimal = Decimal("1000.00")):
        self._accounts: Dict[UUID, TraderAccount] = {}
        self._usernames: set[str] = set()
        self._initial_balance = initial_balance

    def register_trader(self, username: str) -> UUID:
        """Register a new trader account

        Args:
            username (str): The username for the new trader

        Raises:
            ValueError: If username already exists

        Returns:
            UUID: The unique identifier for the trader
        """

        if username in self._usernames:
            raise ValueError(f"Username {username} already exists")

        trader_id = uuid4()
        account = TraderAccount(
            trader_id=trader_id, username=username, balance=self._initial_balance
        )

        self._accounts[trader_id] = account
        self._usernames.add(username)
        return trader_id

    def get_account(self, trader_id: UUID) -> Optional[TraderAccount]:
        """Get trader account details

        Args:
            trader_id (UUID): The UUID of the trader

        Returns:
            Optional[TraderAccount]: The trader's account if found, None otherwise
        """
        return self._accounts.get(trader_id)

    def update_balance(self, trader_id: UUID, amount: Decimal) -> Decimal:
        """Update trader balance

        Args:
            trader_id (UUID): The UUID of the trader
            amount (Decimal): The amount to update (positive for credit, negative for debit)

        Returns:
            Decimal: The new balance

        Raises:
            ValueError: If trader not found or insufficient funds
        """
        account = self.get_account(trader_id)
        if not account:
            raise ValueError(f"Trader {trader_id} not found")

        new_balance = account.balance + amount
        if new_balance < Decimal("0"):
            raise ValueError(f"Insufficient funds for trader {trader_id}")

        account.balance = new_balance
        return new_balance

    def deactivate_account(self, trader_id: UUID) -> None:
        """Deactivate a trader account

        Args:
            trader_id (UUID): The UUID of the trader

        Raises:
            ValueError: If trader not found
        """

        account = self.get_account(trader_id)
        if not account:
            raise ValueError(f"Trader {trader_id} not found")
        account.active = False

    def get_balance(self, trader_id: UUID) -> Decimal:
        """Get the current balance of a trader account

        Args:
            trader_id (UUID): The UUID of the trader

        Raises:
            ValueError: If trader not found

        Returns:
            Decimal: The current balance
        """
        account = self.get_account(trader_id)
        if not account:
            raise ValueError(f"Trader {trader_id} not found")
        return account.balance

    def is_active(self, trader_id: UUID) -> bool:
        """Check if a trader account is active

        Args:
            trader_id (UUID): The UUID of the trader

        Raises:
            ValueError: If trader not found

        Returns:
            bool: True if account is active, False otherwise
        """
        account = self.get_account(trader_id)
        if not account:
            raise ValueError(f"Trader {trader_id} not found")
        return account.active


if __name__ == "__main__":
    from uuid import uuid4

    manager = TraderAccountManager()
    trader_id = manager.register_trader("trader1")
    print(f"Registered trader with ID: {trader_id}")

    balance = manager.get_balance(trader_id)
    print(f"Initial balance: {balance}")

    new_balance = manager.update_balance(trader_id, Decimal("500.00"))
    print(f"Updated balance: {new_balance}")

    is_active = manager.is_active(trader_id)
    print(f"Is account active? {is_active}")

    manager.deactivate_account(trader_id)
    is_active = manager.is_active(trader_id)
    print(f"Is account active after deactivation? {is_active}")
