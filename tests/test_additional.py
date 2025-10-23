import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone

from budget_tracker.models import Expense
from budget_tracker import analytics, persistence


class AdditionalTests(unittest.TestCase):
    def test_calculate_total_empty(self):
        self.assertEqual(0.0, analytics.calculate_total([]))

    def test_totals_by_category_case_insensitive(self):
        items = [
            Expense(description="A", amount=10.0, category="Food"),
            Expense(description="B", amount=5.0, category="food"),
        ]
        totals = analytics.totals_by_category(items)
        self.assertAlmostEqual(15.0, totals.get("food"))

    def test_average_by_category_single(self):
        items = [Expense(description="A", amount=10.0, category="misc")]
        avg = analytics.average_by_category(items)
        self.assertAlmostEqual(10.0, avg.get("misc"))

    def test_persistence_handles_empty_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "expenses.json"
            # ensure empty file exists
            target.write_text("")
            loaded = persistence.load_expenses(target)
            self.assertEqual([], loaded)

    def test_models_from_dict_epoch(self):
        # integer timestamp should be interpreted as UTC epoch seconds
        epoch = 1600000000
        data = {"description": "E", "amount": 1.0, "category": "x", "timestamp": str(epoch)}
        loaded = Expense.from_dict(data)
        self.assertIsNotNone(loaded.timestamp.tzinfo)
        self.assertEqual(loaded.timestamp.tzinfo, timezone.utc)


if __name__ == "__main__":
    unittest.main()
