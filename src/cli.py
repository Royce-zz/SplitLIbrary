"""Command-line interface for the split."""

from __future__ import annotations

import argparse
import datetime
import os
import sys
from decimal import Decimal

from ledger import compute_balances
from simplify import simplify_debts
from splits import equal_split, shares_split
from storage import Storage


def _build_parser() -> argparse.ArgumentParser:
    """Return the top-level argument parser."""
    parser = argparse.ArgumentParser(prog="splitpy")
    parser.add_argument(
        "--store",
        default="splitpy.json",
        help="Path to the JSON store file.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_user = sub.add_parser("add-user", help="Create a new user.")
    p_user.add_argument("--id", required=True)
    p_user.add_argument("--name", required=True)

    p_group = sub.add_parser("add-group", help="Create a new group.")
    p_group.add_argument("--id", required=True)
    p_group.add_argument("--name", required=True)
    p_group.add_argument("--members", nargs="+", required=True)

    p_exp = sub.add_parser("add-expense", help="Record a new expense.")
    p_exp.add_argument("--group", required=True)
    p_exp.add_argument("--description", required=True)
    p_exp.add_argument("--amount", required=True)
    p_exp.add_argument("--paid-by", required=True)
    p_exp.add_argument("--date", default="2024-01-01")
    p_exp.add_argument(
        "--split",
        choices=["equal", "shares"],
        default="equal",
    )
    p_exp.add_argument("--participants", nargs="+", required=True)
    p_exp.add_argument(
        "--values",
        nargs="+",
        default=[],
        help=(
            "Positive integer share counts paired with --participants. "
            "Required when --split is 'shares'; ignored otherwise."
        ),
    )

    p_bal = sub.add_parser("balances", help="Show net balances.")
    p_bal.add_argument("--group", required=True)

    p_settle = sub.add_parser("settle", help="Simplify debts.")
    p_settle.add_argument("--group", required=True)

    return parser


def _build_splits(
    split_type: str,
    amount: Decimal,
    participants: list[str],
    values: list[str],
) -> dict[str, Decimal]:
    """Dispatch to the requested split strategy."""
    if split_type == "equal":
        return equal_split(amount, participants)
    if split_type == "shares":
        if len(values) != len(participants):
            raise ValueError(
                "Number of --values must match number of --participants"
            )
        shares = {p: int(v) for p, v in zip(participants, values)}
        return shares_split(amount, shares)
    raise ValueError(f"Unknown split type: {split_type}")


def _load_storage(path: str) -> Storage:
    """Return a store loaded from ``path`` or a fresh one if missing."""
    if os.path.exists(path):
        return Storage.load(path)
    return Storage()


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return a shell-style exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    storage = _load_storage(args.store)

    if args.command == "add-user":
        storage.add_user(args.id, args.name)
        print(f"Added user {args.id}.")
        storage.save(args.store)

    elif args.command == "add-group":
        storage.add_group(args.id, args.name, args.members)
        print(f"Added group {args.id}.")
        storage.save(args.store)

    elif args.command == "add-expense":
        amount = Decimal(args.amount)
        splits = _build_splits(
            args.split, amount, args.participants, args.values
        )
        storage.add_expense(
            group_id=args.group,
            description=args.description,
            amount=amount,
            paid_by=args.paid_by,
            expense_date=datetime.date.fromisoformat(args.date),
            splits=splits,
        )
        print(f"Added expense of {amount} to group {args.group}.")
        storage.save(args.store)

    elif args.command == "balances":
        expenses = storage.expenses_for_group(args.group)
        balances = compute_balances(expenses)
        for user_id, balance in sorted(balances.items()):
            print(f"{user_id}: {balance}")

    elif args.command == "settle":
        expenses = storage.expenses_for_group(args.group)
        balances = compute_balances(expenses)
        for s in simplify_debts(balances):
            print(f"{s.from_user} -> {s.to_user}: {s.amount}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
