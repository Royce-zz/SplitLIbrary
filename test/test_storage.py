"""Unit tests for the Storage class."""

from __future__ import annotations

import datetime
from decimal import Decimal
from pathlib import Path

import pytest

from storage import Storage


def test_add_user() -> None:
    """Test that an added user can be retrieved from storage."""
    # arrange
    storage = Storage()

    # act
    user = storage.add_user("alice", "Alice Andrews")

    # assert
    assert user.user_id == "alice"
    assert user.full_name == "Alice Andrews"
    assert storage.users["alice"] == user


def test_add_user_duplicate() -> None:
    """Test that adding an existing user id raises ValueError."""
    # arrange
    storage = Storage()
    storage.add_user("alice", "Alice")

    # act and assert
    with pytest.raises(ValueError, match="User already exists: alice"):
        storage.add_user("alice", "Someone Else")


def test_add_group_with_members() -> None:
    """Test that a group and its members are stored correctly."""
    # arrange
    storage = Storage()
    storage.add_user("alice", "Alice")
    storage.add_user("bob", "Bob")

    # act
    group = storage.add_group("trip", "Beach Trip", ["alice", "bob"])

    # assert
    assert group.name == "Beach Trip"
    assert group.member_ids == ["alice", "bob"]


def test_add_group_unknown_member() -> None:
    """Test that adding a group with an unknown member raises."""
    # arrange
    storage = Storage()
    storage.add_user("alice", "Alice")

    # act and assert
    with pytest.raises(ValueError, match="Unknown user in group: ghost"):
        storage.add_group("g", "G", ["alice", "ghost"])


def test_add_expense_stores_splits() -> None:
    """Test that an expense's splits round-trip through storage."""
    # arrange
    storage = Storage()
    storage.add_user("alice", "Alice")
    storage.add_user("bob", "Bob")
    storage.add_group("g", "G", ["alice", "bob"])

    # act
    expense = storage.add_expense(
        group_id="g",
        description="Dinner",
        amount=Decimal("40.00"),
        paid_by="alice",
        expense_date=datetime.date(2024, 5, 1),
        splits={"alice": Decimal("20.00"), "bob": Decimal("20.00")},
    )

    # assert
    assert expense.amount == Decimal("40.00")
    assert expense.paid_by == "alice"
    assert expense.description == "Dinner"
    assert expense.expense_date == datetime.date(2024, 5, 1)
    assert expense.splits == {
        "alice": Decimal("20.00"),
        "bob": Decimal("20.00"),
    }


def test_add_expense_mismatched_splits() -> None:
    """Test that splits must sum to the expense amount."""
    # arrange
    storage = Storage()
    storage.add_user("alice", "Alice")
    storage.add_user("bob", "Bob")
    storage.add_group("g", "G", ["alice", "bob"])

    # act and assert
    with pytest.raises(
        ValueError, match="splits sum to 30.00, expected 40.00"
    ):
        storage.add_expense(
            group_id="g",
            description="Oops",
            amount=Decimal("40.00"),
            paid_by="alice",
            expense_date=datetime.date(2024, 5, 1),
            splits={"alice": Decimal("10.00"), "bob": Decimal("20.00")},
        )


def test_add_expense_unknown_group() -> None:
    """Test that adding an expense for an unknown group raises."""
    # arrange
    storage = Storage()
    storage.add_user("alice", "Alice")

    # act and assert
    with pytest.raises(ValueError, match="Unknown group: ghost"):
        storage.add_expense(
            group_id="ghost",
            description="E",
            amount=Decimal("10.00"),
            paid_by="alice",
            expense_date=datetime.date(2024, 5, 1),
            splits={"alice": Decimal("10.00")},
        )


def test_add_expense_unknown_payer() -> None:
    """Test that adding an expense with an unknown payer raises."""
    # arrange
    storage = Storage()
    storage.add_user("alice", "Alice")
    storage.add_group("g", "G", ["alice"])

    # act and assert
    with pytest.raises(ValueError, match="Unknown payer: ghost"):
        storage.add_expense(
            group_id="g",
            description="E",
            amount=Decimal("10.00"),
            paid_by="ghost",
            expense_date=datetime.date(2024, 5, 1),
            splits={"alice": Decimal("10.00")},
        )


def test_expenses_for_group_filters_by_group() -> None:
    """Test expenses_for_group returns only matching expenses."""
    # arrange
    storage = Storage()
    storage.add_user("alice", "Alice")
    storage.add_group("g1", "G1", ["alice"])
    storage.add_group("g2", "G2", ["alice"])
    storage.add_expense(
        group_id="g1",
        description="E1",
        amount=Decimal("10.00"),
        paid_by="alice",
        expense_date=datetime.date(2024, 1, 1),
        splits={"alice": Decimal("10.00")},
    )
    storage.add_expense(
        group_id="g2",
        description="E2",
        amount=Decimal("20.00"),
        paid_by="alice",
        expense_date=datetime.date(2024, 1, 1),
        splits={"alice": Decimal("20.00")},
    )

    # act
    g1 = storage.expenses_for_group("g1")
    g2 = storage.expenses_for_group("g2")

    # assert
    assert len(g1) == 1 and g1[0].description == "E1"
    assert len(g2) == 1 and g2[0].description == "E2"


def test_save_and_load_round_trip(tmp_path: Path) -> None:
    """Test that saving and reloading preserves all data."""
    # arrange
    storage = Storage()
    storage.add_user("alice", "Alice")
    storage.add_user("bob", "Bob")
    storage.add_group("g", "Trip", ["alice", "bob"])
    storage.add_expense(
        group_id="g",
        description="Dinner",
        amount=Decimal("40.00"),
        paid_by="alice",
        expense_date=datetime.date(2024, 5, 1),
        splits={"alice": Decimal("20.00"), "bob": Decimal("20.00")},
    )
    filename = str(tmp_path / "splitpy.json")

    # act
    storage.save(filename)
    reloaded = Storage.load(filename)

    # assert
    assert reloaded.users == storage.users
    assert reloaded.groups == storage.groups
    assert reloaded.expenses == storage.expenses
