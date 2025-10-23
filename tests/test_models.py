import unittest
from datetime import datetime, timezone

from budget_tracker.models import Expense


class ModelsTests(unittest.TestCase):
    def test_expense_serialization_roundtrip(self):
        exp = Expense(description="T", amount=1.23, category="misc")
        data = exp.to_dict()
        self.assertIn("timestamp", data)
        loaded = Expense.from_dict(data)
        self.assertAlmostEqual(loaded.amount, exp.amount)
        # timestamp should be timezone-aware
        self.assertIsNotNone(loaded.timestamp.tzinfo)
        self.assertEqual(loaded.timestamp.tzinfo, timezone.utc)


if __name__ == "__main__":
    unittest.main()
