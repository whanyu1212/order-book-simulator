from uuid import UUID, uuid4
from decimal import Decimal
from typing import Dict, Optional
from order_book_simulator.config.account import TraderAccount
from order_book_simulator.database.session import get_db
from order_book_simulator.database.models import DBTraderAccount


class TraderAccountManager:
    """Manages trader accounts, balances, and registration"""

    def __init__(self, initial_balance: Decimal = Decimal("1000.00")):
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
        with get_db() as db:
            # Check if username exists
            existing_account = (
                db.query(DBTraderAccount)
                .filter(DBTraderAccount.username == username)
                .first()
            )
            if existing_account:
                raise ValueError(f"Username {username} already exists")

            trader_id = uuid4()
            db_account = DBTraderAccount(
                trader_id=str(trader_id),
                username=username,
                balance=self._initial_balance,
                active=True,
            )
            db.add(db_account)
            db.commit()
            return trader_id

    def get_account(self, trader_id: UUID) -> Optional[TraderAccount]:
        """Get trader account details

        Args:
            trader_id (UUID): The UUID of the trader

        Returns:
            Optional[TraderAccount]: The trader's account if found, None otherwise
        """
        with get_db() as db:
            db_account = (
                db.query(DBTraderAccount)
                .filter(DBTraderAccount.trader_id == str(trader_id))
                .first()
            )
            if not db_account:
                return None
            return TraderAccount(
                trader_id=UUID(db_account.trader_id),
                username=db_account.username,
                balance=db_account.balance,
                active=db_account.active,
            )

    def get_trader_by_username(self, username: str) -> Optional[TraderAccount]:
        """Get trader account details by username"""
        with get_db() as db:
            db_account = (
                db.query(DBTraderAccount)
                .filter(DBTraderAccount.username == username)
                .first()
            )
            if not db_account:
                return None
            return TraderAccount(
                trader_id=UUID(db_account.trader_id),
                username=db_account.username,
                balance=db_account.balance,
                active=db_account.active,
            )

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
        with get_db() as db:
            db_account = (
                db.query(DBTraderAccount)
                .filter(DBTraderAccount.trader_id == str(trader_id))
                .first()
            )
            if not db_account:
                raise ValueError(f"Trader {trader_id} not found")

            new_balance = db_account.balance + amount
            if new_balance < Decimal("0"):
                raise ValueError(f"Insufficient funds for trader {trader_id}")

            db_account.balance = new_balance
            db.commit()
            return new_balance

    def deactivate_account(self, trader_id: UUID) -> None:
        """Deactivate a trader account

        Args:
            trader_id (UUID): The UUID of the trader

        Raises:
            ValueError: If trader not found
        """
        with get_db() as db:
            db_account = (
                db.query(DBTraderAccount)
                .filter(DBTraderAccount.trader_id == str(trader_id))
                .first()
            )
            if not db_account:
                raise ValueError(f"Trader {trader_id} not found")
            db_account.active = False
            db.commit()

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
