"""Unit tests for the ledger module."""

from __future__ import annotations
import datetime
from decimal import Decimal

from ledger import compute_balances
from storage import Storage


def test_compute_balances_single_expense() -> None:
    """Test compute_balances with one expense paid by one user."""
    # arrange
    storage = Storage()
    storage.add_user("alice", "Alice")
    storage.add_user("bob", "Bob")
    storage.add_user("carol", "Carol")
    storage.add_group("trip", "Beach Trip", ["alice", "bob", "carol"])
    storage.add_expense(
        group_id="trip",
        description="Dinner",
        amount=Decimal("90.00"),
        paid_by="alice",
        expense_date=datetime.date(2024, 1, 1),
        splits={
            "alice": Decimal("30.00"),
            "bob": Decimal("30.00"),
            "carol": Decimal("30.00"),
        },
    )

    # act
    balances = compute_balances(storage.expenses_for_group("trip"))

    # assert
    assert balances == {
        "alice": Decimal("60.00"),
        "bob": Decimal("-30.00"),
        "carol": Decimal("-30.00"),
    }


def test_compute_balances_multiple_expenses() -> None:
    """Test compute_balances accumulates across multiple payers."""
    # arrange
    storage = Storage()
    for uid, name in [("a", "A"), ("b", "B"), ("c", "C")]:
        storage.add_user(uid, name)
    storage.add_group("g", "G", ["a", "b", "c"])
    storage.add_expense(
        group_id="g",
        description="E1",
        amount=Decimal("90.00"),
        paid_by="a",
        expense_date=datetime.date(2024, 1, 1),
        splits={
            "a": Decimal("30.00"),
            "b": Decimal("30.00"),
            "c": Decimal("30.00"),
        },
    )
    storage.add_expense(
        group_id="g",
        description="E2",
        amount=Decimal("60.00"),
        paid_by="b",
        expense_date=datetime.date(2024, 1, 2),
        splits={
            "a": Decimal("20.00"),
            "b": Decimal("20.00"),
            "c": Decimal("20.00"),
        },
    )
    storage.add_expense(
        group_id="g",
        description="E3",
        amount=Decimal("300.00"),
        paid_by="c",
        expense_date=datetime.date(2024, 1, 3),
        splits={
            "a": Decimal("100.00"),
            "b": Decimal("100.00"),
            "c": Decimal("100.00"),
        },
    )

    # act
    balances = compute_balances(storage.expenses_for_group("g"))

    # assert:
    assert balances == {
        "a": Decimal("-60.00"),
        "b": Decimal("-90.00"),
        "c": Decimal("150.00"),
    }
