"""Unit tests for the debt simplification algorithm."""

from __future__ import annotations
from decimal import Decimal

import pytest

from models import Settlement
from simplify import simplify_debts


def test_simplify_debts_two_users() -> None:
    """Test simplify_debts on a simple two-user ledger."""
    # arrange
    balances = {"alice": Decimal("30"), "bob": Decimal("-30")}

    # act
    settlements = simplify_debts(balances)

    # assert
    assert settlements == [Settlement("bob", "alice", Decimal("30"))]


def test_simplify_debts_three_users_one_creditor() -> None:
    """Test simplify_debts when one creditor receives from two debtors."""
    # arrange
    balances = {
        "alice": Decimal("60"),
        "bob": Decimal("-30"),
        "carol": Decimal("-30"),
    }

    # act
    settlements = simplify_debts(balances)

    # assert: alice is paid twice; order depends on dict iteration.
    assert len(settlements) == 2
    assert Settlement("bob", "alice", Decimal("30")) in settlements
    assert Settlement("carol", "alice", Decimal("30")) in settlements


def test_simplify_debts_three_users_chain() -> None:
    """Test simplify_debts when amounts do not match evenly."""
    # arrange: alice is owed 50, bob owes 20, carol owes 30.
    balances = {
        "alice": Decimal("50"),
        "bob": Decimal("-20"),
        "carol": Decimal("-30"),
    }

    # act
    settlements = simplify_debts(balances)

    # assert
    assert len(settlements) == 2
    assert Settlement("carol", "alice", Decimal("30")) in settlements
    assert Settlement("bob", "alice", Decimal("20")) in settlements


def test_simplify_debts_five_users() -> None:
    """Test simplify_debts on a five-user ledger with mixed positions."""
    # arrange: two creditors, three debtors. Sum is zero.
    balances = {
        "alice": Decimal("80"),
        "bob": Decimal("40"),
        "carol": Decimal("-30"),
        "dave": Decimal("-50"),
        "eve": Decimal("-40"),
    }

    # act
    settlements = simplify_debts(balances)

    # assert: 3 settlements -- dave->alice(50), eve->bob(40), carol->alice(30)
    assert len(settlements) == 3
    assert Settlement("dave", "alice", Decimal("50")) in settlements
    assert Settlement("eve", "bob", Decimal("40")) in settlements
    assert Settlement("carol", "alice", Decimal("30")) in settlements


def test_simplify_debts_empty_ledger() -> None:
    """Test simplify_debts on an empty balance dict."""
    # act
    settlements = simplify_debts({})

    # assert
    assert settlements == []


def test_simplify_debts_nonzero_total() -> None:
    """Test rejection works for non-zero sums across multiple users."""
    # act and assert
    with pytest.raises(ValueError, match="must sum to zero"):
        simplify_debts({"alice": Decimal("10"), "bob": Decimal("-5")})
