"""Unit tests for the split strategies."""

from __future__ import annotations
from decimal import Decimal

import pytest

from splits import equal_split, shares_split


def test_equal_split_even_amount() -> None:
    """Test equal_split when the amount divides evenly."""
    # arrange
    amount = Decimal("90.00")
    participants = ["alice", "bob", "carol"]

    # act
    result = equal_split(amount, participants)

    # assert
    assert result == {
        "alice": Decimal("30.00"),
        "bob": Decimal("30.00"),
        "carol": Decimal("30.00"),
    }


def test_equal_split_with_remainder() -> None:
    """Test equal_split distributes leftover one cents."""
    # arrange
    amount = Decimal("10.00")
    participants = ["alice", "bob", "carol"]

    # act
    result = equal_split(amount, participants)

    # assert
    assert sum(result.values()) == amount
    assert result["alice"] == Decimal("3.34")
    assert result["bob"] == Decimal("3.33")
    assert result["carol"] == Decimal("3.33")


def test_equal_split_with_remainder() -> None:
    """Test equal_split distributes leftover two cents."""
    # arrange
    amount = Decimal("10.01")
    participants = ["alice", "bob", "carol"]

    # act
    result = equal_split(amount, participants)

    # assert
    assert sum(result.values()) == amount
    assert result["alice"] == Decimal("3.33")
    assert result["bob"] == Decimal("3.34")
    assert result["carol"] == Decimal("3.34")


def test_equal_split_empty_participants() -> None:
    """Test equal_split raises when participants is empty."""
    # act and assert
    with pytest.raises(ValueError, match="participants must not be empty"):
        equal_split(Decimal("10.00"), [])


def test_equal_split_negative_amount() -> None:
    """Test equal_split raises when amount is negative."""
    # act and assert
    with pytest.raises(ValueError, match="amount must be non-negative"):
        equal_split(Decimal("-1.00"), ["alice"])


def test_shares_split_basic() -> None:
    """Test shares_split with a 2:1 share ratio."""
    # arrange
    amount = Decimal("30.00")
    shares = {"alice": 2, "bob": 1}

    # act
    result = shares_split(amount, shares)

    # assert
    assert result == {
        "alice": Decimal("20.00"),
        "bob": Decimal("10.00"),
    }


def test_shares_split_with_remainder() -> None:
    """Test shares_split distributes leftover cents correctly."""
    # arrange
    amount = Decimal("10.00")
    shares = {"alice": 2, "bob": 1}

    # act
    result = shares_split(amount, shares)

    # assert
    assert result == {
        "alice": Decimal("6.67"),
        "bob": Decimal("3.33"),
    }


def test_shares_split_empty() -> None:
    """Test shares_split raises when shares is empty."""
    # act and assert
    with pytest.raises(ValueError, match="shares must not be empty"):
        shares_split(Decimal("10.00"), {})


def test_shares_split_negative_amount() -> None:
    """Test shares_split raises when amount is negative."""
    # act and assert
    with pytest.raises(ValueError, match="amount must be non-negative"):
        shares_split(Decimal("-1.00"), {"alice": 1})


def test_shares_split_rejects_zero_share() -> None:
    """Test shares_split raises on a zero share count."""
    # act and assert
    with pytest.raises(ValueError, match="positive integers"):
        shares_split(Decimal("10.00"), {"alice": 0, "bob": 1})


def test_shares_split_rejects_negative_share() -> None:
    """Test shares_split raises on a negative share count."""
    # act and assert
    with pytest.raises(ValueError, match="positive integers"):
        shares_split(Decimal("10.00"), {"alice": -1, "bob": 2})
