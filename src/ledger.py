"""Ledger: compute net per-user balances from a list of expenses."""

from __future__ import annotations
from decimal import Decimal

from models import Expense


def compute_balances(expenses: list[Expense]) -> dict[str, Decimal]:
    """Compute the net balance for every user in the expenses."""
    balances: dict[str, Decimal] = {}

    for expense in expenses:
        amount = expense.amount
        paid_by = expense.paid_by
        balances[paid_by] = balances.get(paid_by, Decimal("0")) + amount

        for user_id, share in expense.splits.items():
            balances[user_id] = balances.get(user_id, Decimal("0")) - share

    return {u: b for u, b in balances.items() if b != 0}