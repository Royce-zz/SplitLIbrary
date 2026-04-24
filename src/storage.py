"""In-memory storage for splitpy"""

from __future__ import annotations
import datetime
import json
import uuid
from decimal import Decimal

from models import Expense, Group, User


class Storage:
    """In-memory store for users, groups, and expenses."""

    def __init__(self) -> None:
        """Initialize an empty store."""
        self.users: dict[str, User] = {}
        self.groups: dict[str, Group] = {}
        self.expenses: dict[str, Expense] = {}

    def add_user(self, user_id: str, full_name: str) -> User:
        """Insert a user and return it."""
        if user_id in self.users:
            raise ValueError(f"User already exists: {user_id}")
        user = User(user_id, full_name)
        self.users[user_id] = user
        return user

    def add_group(
        self,
        group_id: str,
        name: str,
        member_ids: list[str],
    ) -> Group:
        """Insert a group and return it."""
        if group_id in self.groups:
            raise ValueError(f"Group already exists: {group_id}")
        for uid in member_ids:
            if uid not in self.users:
                raise ValueError(f"Unknown user in group: {uid}")
        group = Group(group_id, name, list(member_ids))
        self.groups[group_id] = group
        return group

    def add_expense(
        self,
        group_id: str,
        description: str,
        amount: Decimal,
        paid_by: str,
        expense_date: datetime.date,
        splits: dict[str, Decimal],
    ) -> Expense:
        """Insert an expense with the given splits and return it."""
        if group_id not in self.groups:
            raise ValueError(f"Unknown group: {group_id}")
        if paid_by not in self.users:
            raise ValueError(f"Unknown payer: {paid_by}")
        total = sum(splits.values(), Decimal("0"))
        if total != amount:
            raise ValueError(f"splits sum to {total}, expected {amount}")

        expense_id = str(uuid.uuid4())
        expense = Expense(
            expense_id=expense_id,
            group_id=group_id,
            description=description,
            amount=amount,
            paid_by=paid_by,
            expense_date=expense_date,
            splits=dict(splits),
        )
        self.expenses[expense_id] = expense
        return expense

    def expenses_for_group(self, group_id: str) -> list[Expense]:
        """Return every expense that belongs to ``group_id``."""
        return [e for e in self.expenses.values() if e.group_id == group_id]

    def save(self, filename: str) -> None:
        """Save the store to a JSON file."""
        data = {
            "users": [
                {"user_id": u.user_id, "full_name": u.full_name}
                for u in self.users.values()
            ],
            "groups": [
                {
                    "group_id": g.group_id,
                    "name": g.name,
                    "member_ids": g.member_ids,
                }
                for g in self.groups.values()
            ],
            "expenses": [
                {
                    "expense_id": e.expense_id,
                    "group_id": e.group_id,
                    "description": e.description,
                    "amount": str(e.amount),
                    "paid_by": e.paid_by,
                    "expense_date": e.expense_date.isoformat(),
                    "splits": {uid: str(amt) for uid, amt in e.splits.items()},
                }
                for e in self.expenses.values()
            ],
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, filename: str) -> "Storage":
        """Load a store from a JSON file previously writtenn."""
        with open(filename) as f:
            data = json.load(f)

        storage = cls()
        for u in data["users"]:
            storage.add_user(u["user_id"], u["full_name"])
        for g in data["groups"]:
            storage.add_group(g["group_id"], g["name"], list(g["member_ids"]))
        for e in data["expenses"]:
            expense = Expense(
                expense_id=e["expense_id"],
                group_id=e["group_id"],
                description=e["description"],
                amount=Decimal(e["amount"]),
                paid_by=e["paid_by"],
                expense_date=datetime.date.fromisoformat(e["expense_date"]),
                splits={uid: Decimal(amt) for uid, amt in e["splits"].items()},
            )
            storage.expenses[expense.expense_id] = expense
        return storage
