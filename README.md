# SplitLIbrary

This project is a Python library for splitting expenses among a
group of friends, roommates, or travelers. It is able to run using
a command-line interface.

The library allows the following work:
- creating users and groups
- recording expenses with either equal or share-based splits
- computing the net balance of each user in a group
- simplifying debts into the smallest practical set of payments

## For end users

### Installation

```bash
git clone https://github.com/Royce-zz/Split_Library
cd Split_Library

python3 -m venv .venv
source .venv/bin/activate       # macOS / Linux
.\.venv\Scripts\activate        # Windows

pip install -r requirements-test.txt
```

### Data Format
`User`, `Group`, `Expense`, and `Settlement` are plain Python
classes that hold their attributes directly. `Storage` keeps 
everything in local dictionaries and can be saved to or loaded 
from a JSON file via `Storage.save(path)` and `Storage.load(path)`.

### Split strategies

`splitpy` supports two ways of dividing an expense:

- `equal` participants only, Every participant owes the same amount
- `shares` positive integer shares, Each user owes a share of the total

In both strategies, any cent-level rounding remainder is
distributed one cent at a time to participants in the order they
were given.

### Example

```python
import datetime
from decimal import Decimal

from ledger import compute_balances
from simplify import simplify_debts
from splits import equal_split, shares_split
from storage import Storage

storage = Storage()
storage.add_user("alice", "Alice")
storage.add_user("bob", "Bob")
storage.add_user("carol", "Carol")
storage.add_group("trip", "Beach Trip", ["alice", "bob", "carol"])

# An equal-split expense.
amount = Decimal("90.00")
storage.add_expense(
    group_id="trip",
    description="Dinner",
    amount=amount,
    paid_by="alice",
    expense_date=datetime.date(2024, 7, 12),
    splits=equal_split(amount, ["alice", "bob", "carol"]),
)

# A share-based expense: alice pays double.
rent = Decimal("1200.00")
storage.add_expense(
    group_id="trip",
    description="Rental house",
    amount=rent,
    paid_by="alice",
    expense_date=datetime.date(2024, 7, 12),
    splits=shares_split(rent, {"alice": 2, "bob": 1, "carol": 1}),
)

balances = compute_balances(storage.expenses_for_group("trip"))
for payment in simplify_debts(balances):
    print(f"{payment.from_user} -> {payment.to_user}: {payment.amount}")
```

### Command-line interface

Every time you run the CLI, your data (users, groups, expenses) 
is saved to one JSON file on your hard drive. 
The `--store` flag tells the CLI which file to use.

```bash
python src/cli.py --store splitpy.json add-user --id alice --name "Alice"
python src/cli.py --store splitpy.json add-user --id bob --name "Bob"
python src/cli.py --store splitpy.json add-group --id trip --name Beach \
    --members alice bob

# Equal split (the default).
python src/cli.py --store splitpy.json add-expense \
    --group trip --description "Dinner" \
    --amount 40.00 --paid-by alice \
    --split equal --participants alice bob

# Shares split: alice pays twice as much as bob.
python src/cli.py --store splitpy.json add-expense \
    --group trip --description "Rent" \
    --amount 1200.00 --paid-by alice \
    --split shares --participants alice bob --values 2 1

python src/cli.py --store splitpy.json balances --group trip
python src/cli.py --store splitpy.json settle --group trip
```


## For contributors

### Local testing

```bash
pip install -r requirements-test.txt
pip install ruff mypy
ruff check .
mypy src
pytest --cov=src --cov-report=term-missing
```

All tests live in `tests/` and their filenames start with `test_`.
**Python 3.10 or higher is required.**

### Continuous integration

The GitHub Actions workflow at `.github/workflows/test.yml` runs
`ruff`, `mypy`, and the full `pytest` suite with coverage on every
push and pull request.

