"""Major class for the splitpy expense-splitting library."""

from __future__ import annotations
import datetime
from decimal import Decimal


class User:
    """A single user with an id and full name."""

    def __init__(self, user_id: str, full_name: str) -> None:
        """Initialize a User object."""
        self.user_id = user_id
        self.full_name = full_name

    def __eq__(self, other: object) -> bool:
        """Return whether two User objects are equal."""
        if not isinstance(other, User):
            return NotImplemented
        return (
            self.user_id == other.user_id and self.full_name == other.full_name
        )

    def __hash__(self) -> int:
        """Return the hash of the user id."""
        return hash(self.user_id)


class Group:
    """A named group of users that share expenses."""

    def __init__(
        self,
        group_id: str,
        name: str,
        member_ids: list[str],
    ) -> None:
        """Initialize a Group object."""
        self.group_id = group_id
        self.name = name
        self.member_ids = member_ids

    def __eq__(self, other: object) -> bool:
        """Return whether two Group objects are equal."""
        if not isinstance(other, Group):
            return NotImplemented
        return (
            self.group_id == other.group_id
            and self.name == other.name
            and self.member_ids == other.member_ids
        )


class Expense:
    """A single expense paid by one user on behalf of a group.

    The full amount was paid by ``paid_by``. The ``splits`` dictionary
    maps each participating user_id to the portion they owe. The sum
    of split values must equal ``amount``.
    """

    def __init__(
        self,
        expense_id: str,
        group_id: str,
        description: str,
        amount: Decimal,
        paid_by: str,
        expense_date: datetime.date,
        splits: dict[str, Decimal],
    ) -> None:
        """Initialize an Expense object."""
        self.expense_id = expense_id
        self.group_id = group_id
        self.description = description
        self.amount = amount
        self.paid_by = paid_by
        self.expense_date = expense_date
        self.splits = splits

    def __eq__(self, other: object) -> bool:
        """Return whether two Expense objects are equal."""
        if not isinstance(other, Expense):
            return NotImplemented
        return (
            self.expense_id == other.expense_id
            and self.group_id == other.group_id
            and self.description == other.description
            and self.amount == other.amount
            and self.paid_by == other.paid_by
            and self.expense_date == other.expense_date
            and self.splits == other.splits
        )


class Settlement:
    """A single proposed payment that moves money between two users."""

    def __init__(
        self,
        from_user: str,
        to_user: str,
        amount: Decimal,
    ) -> None:
        """Initialize a Settlement object."""
        self.from_user = from_user
        self.to_user = to_user
        self.amount = amount

    def __eq__(self, other: object) -> bool:
        """Return whether two Settlement objects are equal."""
        if not isinstance(other, Settlement):
            return NotImplemented
        return (
            self.from_user == other.from_user
            and self.to_user == other.to_user
            and self.amount == other.amount
        )

    def __repr__(self) -> str:
        """Return a developer-readable representation of the settlement."""
        return (
            f"Settlement(from_user={self.from_user!r}, "
            f"to_user={self.to_user!r}, amount={self.amount})"
        )
