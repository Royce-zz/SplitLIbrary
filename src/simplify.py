"""Debt simplification."""

from __future__ import annotations
from decimal import Decimal

from models import Settlement

CENT = Decimal("0.01")


def _validate_balances(balances: dict[str, Decimal]) -> None:
    """Raise ValueError if balances do not sum to zero."""
    total = sum(balances.values(), Decimal("0"))
    if total != 0:
        raise ValueError(f"balances must sum to zero, got {total}")


def simplify_debts(
    balances: dict[str, Decimal],
) -> list[Settlement]:
    """Produce a list of settlements."""
    _validate_balances(balances)

    remaining = {u: b for u, b in balances.items() if b != 0}
    settlements: list[Settlement] = []

    while remaining:
        creditor = max(remaining, key=lambda u: remaining[u])
        debtor = min(remaining, key=lambda u: remaining[u])

        amount = min(remaining[creditor], -remaining[debtor])
        settlements.append(Settlement(debtor, creditor, amount))

        remaining[creditor] -= amount
        remaining[debtor] += amount

        if abs(remaining[creditor]) < CENT:
            del remaining[creditor]
        if debtor in remaining and abs(remaining[debtor]) < CENT:
            del remaining[debtor]

    return settlements
