"""Split Functions."""

from __future__ import annotations
from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def _round_cents(value: Decimal) -> Decimal:
    """Round a decimal to two decimal places (half-up)."""
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def _distribute_remainder(
    amounts: dict[str, Decimal],
    total: Decimal,
    order: list[str],
) -> dict[str, Decimal]:
    """Adjust the per-user amounts so their sum equals ``total``.

    Returns:
        A new dict with adjusted amounts whose values sum to ``total``.
    """
    adjusted = dict(amounts)
    diff = _round_cents(total) - sum(adjusted.values(), Decimal("0"))
    step = CENT if diff > 0 else -CENT
    i = 0
    while diff != 0 and order:
        user_id = order[i % len(order)]
        adjusted[user_id] = adjusted[user_id] + step
        diff -= step
        i += 1
    return adjusted


def equal_split(amount: Decimal, participants: list[str]) -> dict[str, Decimal]:
    """Split amount equally across participants."""
    if not participants:
        raise ValueError("participants must not be empty")
    if amount < 0:
        raise ValueError(f"amount must be non-negative: {amount}")

    share = _round_cents(amount / Decimal(len(participants)))
    amounts = {user_id: share for user_id in participants}
    return _distribute_remainder(amounts, amount, participants)


def shares_split(amount: Decimal, shares: dict[str, int]) -> dict[str, Decimal]:
    """Split amount by integer shares."""
    if not shares:
        raise ValueError("shares must not be empty")
    if amount < 0:
        raise ValueError(f"amount must be non-negative: {amount}")
    if any(s <= 0 for s in shares.values()):
        raise ValueError("share values must be positive integers")

    total_shares = Decimal(sum(shares.values()))
    amounts = {
        user_id: _round_cents(amount * Decimal(s) / total_shares)
        for user_id, s in shares.items()
    }
    return _distribute_remainder(amounts, amount, list(shares))
