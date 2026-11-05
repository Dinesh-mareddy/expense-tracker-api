"""Expense Tracker REST API - Step 1: database + add and list expenses."""
import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)
DATABASE = "expenses.db"


def get_connection():
    """Open a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # lets us read rows like dictionaries
    return conn


def init_db():
    """Create the expenses table if it does not exist yet."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL
            )
            """
        )


@app.route("/")
def home():
    return jsonify({"message": "Expense Tracker API is running"})


@app.route("/expenses", methods=["POST"])
def add_expense():
    """Add a new expense. Expects JSON: title, amount, category, date."""
    data = request.get_json(silent=True) or {}
    required = ["title", "amount", "category", "date"]
    missing = [field for field in required if field not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        amount = float(data["amount"])
    except (TypeError, ValueError):
        return jsonify({"error": "amount must be a number"}), 400

    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO expenses (title, amount, category, date) VALUES (?, ?, ?, ?)",
            (data["title"], amount, data["category"], data["date"]),
        )
        new_id = cursor.lastrowid

    return jsonify({"id": new_id, "message": "Expense added"}), 201


@app.route("/expenses", methods=["GET"])
def list_expenses():
    """Return all expenses as a JSON list."""
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM expenses ORDER BY date DESC").fetchall()
    return jsonify([dict(row) for row in rows])


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
