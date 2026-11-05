"""Basic tests. Run with: python -m unittest"""
import os
import tempfile
import unittest

import app as expense_app


class ExpenseApiTests(unittest.TestCase):
    def setUp(self):
        self.db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_file.close()
        expense_app.DATABASE = self.db_file.name
        expense_app.init_db()
        self.client = expense_app.app.test_client()

    def tearDown(self):
        os.remove(self.db_file.name)

    def add(self, title="Lunch", amount=100, category="Food", date="2026-11-06"):
        return self.client.post(
            "/expenses",
            json={"title": title, "amount": amount, "category": category, "date": date},
        )

    def test_add_and_get(self):
        response = self.add()
        self.assertEqual(response.status_code, 201)
        expense_id = response.get_json()["id"]
        fetched = self.client.get(f"/expenses/{expense_id}").get_json()
        self.assertEqual(fetched["title"], "Lunch")

    def test_validation_errors(self):
        self.assertEqual(self.client.post("/expenses", json={"title": "x"}).status_code, 400)
        self.assertEqual(self.add(amount="abc").status_code, 400)
        self.assertEqual(self.add(amount=-5).status_code, 400)

    def test_update_and_delete(self):
        expense_id = self.add().get_json()["id"]
        updated = self.client.put(
            f"/expenses/{expense_id}",
            json={"title": "Dinner", "amount": 250, "category": "Food", "date": "2026-11-06"},
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(self.client.get(f"/expenses/{expense_id}").get_json()["title"], "Dinner")
        self.assertEqual(self.client.delete(f"/expenses/{expense_id}").status_code, 200)
        self.assertEqual(self.client.get(f"/expenses/{expense_id}").status_code, 404)

    def test_filters_and_summary(self):
        self.add(amount=100, category="Food", date="2026-11-06")
        self.add(amount=50, category="Travel", date="2026-11-07")
        self.add(amount=30, category="Food", date="2026-10-01")
        food = self.client.get("/expenses?category=Food").get_json()
        self.assertEqual(len(food), 2)
        summary = self.client.get("/summary?month=2026-11").get_json()
        self.assertEqual(summary["total_spent"], 150)
        self.assertEqual(summary["by_category"], {"Food": 100, "Travel": 50})


if __name__ == "__main__":
    unittest.main()
