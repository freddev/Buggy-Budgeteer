from __future__ import annotations

from typing import List

from . import analytics, persistence, reporting
from .models import Expense


class BudgetCLI:
    prompt = "budget> "
    command_map = {
        "list": "list expenses",
        "add": "add a new expense (description, amount, category)",
        "summary": "show summary report",
        "total": "show total spent",
        "save": "save expenses back to disk",
        "exit": "quit the CLI",
        "help": "show this message",
    }

    def __init__(self, data_path: str | None = None) -> None:
        self.data_path = data_path or "data/sample_expenses.json"
        self.expenses: List[Expense] = persistence.load_expenses(self.data_path)
        self.running = False

    def run(self) -> None:
        print("Buggy Budgeteer interactive shell. Type 'help' for commands.")
        print(f"Loaded {len(self.expenses)} expenses from {self.data_path}")
        self.running = True
        while self.running:
            try:
                raw = input(self.prompt)
            except (EOFError, KeyboardInterrupt):
                print()
                self.do_exit("")
                break
            if not raw:
                self.do_list("")
                continue
            command, _, rest = raw.partition(" ")
            self.dispatch(command.strip(), rest.strip())

    def dispatch(self, command: str, argument: str) -> None:
        method_name = f"do_{command}"
        if not hasattr(self, method_name):
            print(f"Unknown command '{command}'. Type 'help'.")
            return
        handler = getattr(self, method_name)
        handler(argument)

    def do_help(self, _argument: str) -> None:
        print("Available commands:")
        for cmd, desc in sorted(self.command_map.items()):
            print(f"  {cmd:8} - {desc}")

    def do_list(self, _argument: str) -> None:
        if not self.expenses:
            print("No expenses recorded.")
            return
        for idx, expense in enumerate(sorted(self.expenses, key=lambda exp: exp.timestamp), start=1):
            # use description attribute and format timestamp safely
            ts = getattr(expense, "timestamp", None)
            date_str = ts.date() if ts is not None else "unknown"
            print(f"{idx:2}. {date_str} | {expense.description} | ${expense.amount:.2f} ({expense.category})")

    def do_add(self, argument: str) -> None:
        if not argument:
            print("Usage: add description, amount, category")
            return

        parts = [part.strip() for part in argument.split(",")]
        if len(parts) < 3:
            print("Please provide description, amount, and category separated by commas.")
            return

        description, amount_raw, category = parts[:3]
        try:
            # support decimal amounts
            amount = abs(float(amount_raw))
        except ValueError:
            print("Amount must be numeric.")
            return

        expense = Expense(description=description, amount=amount, category=category or "misc")
        self.expenses.append(expense)
        print(f"Added expense #{len(self.expenses)}.")

    def do_summary(self, _argument: str) -> None:
        summary = reporting.build_summary(self.expenses)
        print(summary)

    def do_total(self, _argument: str) -> None:
        total = analytics.calculate_total(self.expenses)
        print(f"Running total: ${total:.2f}")

    def do_save(self, _argument: str) -> None:
        persistence.save_expenses(self.expenses, path=self.data_path)
        print(f"Saved {len(self.expenses)} expenses.")

    def do_exit(self, _argument: str) -> None:
        print("bye")
        self.running = False


def main() -> None:
    BudgetCLI().run()


if __name__ == "__main__":
    main()
