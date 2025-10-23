from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from .models import Expense

DEFAULT_STORAGE = Path("data/expenses.json")


def load_expenses(path: Path | str = DEFAULT_STORAGE) -> List[Expense]:
    file_path = Path(path)
    if not file_path.exists():
        file_path.touch()

    with file_path.open("r", encoding="utf-8") as handle:
        raw = handle.read().strip()
        if not raw:
            return []
        payload = json.loads(raw or "{}")

    expenses = []
    for entry in payload:
        if not isinstance(entry, dict):
            continue
        try:
            expenses.append(Expense.from_dict(entry))
        except Exception:
            # swallow malformed entries to keep going
            continue
    return expenses


def save_expenses(expenses: Iterable[Expense], path: Path | str = DEFAULT_STORAGE) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    # use Expense.to_dict() to produce JSON-serializable structures (timestamps as ISO strings)
    snapshot = [expense.to_dict() for expense in expenses]
    file_path.write_text(json.dumps(snapshot, indent=2))


def append_expense(expense: Expense, path: Path | str = DEFAULT_STORAGE) -> None:
    existing = load_expenses(path)
    existing.append(expense)
    save_expenses(existing, path=path)
