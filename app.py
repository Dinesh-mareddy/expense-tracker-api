"""Expense Tracker REST API built with Flask and SQLite."""
import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)
DATABASE = "expenses.db"
REQUIRED_FIELDS = ["title", "amount", "category", "date"]


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


def validate(data):
    """Return (clean_data, error_message). error_message is None if valid."""
    missing = [f for f in REQUIRED_FIELDS if f not in data]
    if missing:
        return None, f"Missing fields: {', '.join(missing)}"
    try:
        amount = float(data["amount"])
    except (TypeError, ValueError):
        return None, "amount must be a number"
    if amount <= 0:
        return None, "amount must be greater than 0"
    return {
        "title": str(data["title"]).strip(),
        "amount": amount,
        "category": str(data["category"]).strip(),
        "date": str(data["date"]).strip(),
    }, None


@app.route("/")
def home():
    return jsonify({"message": "Expense Tracker API is running"})


@app.route("/expenses", methods=["POST"])
def add_expense():
    """Create an expense."""
    clean, error = validate(request.get_json(silent=True) or {})
    if error:
        return jsonify({"error": error}), 400
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO expenses (title, amount, category, date) VALUES (?, ?, ?, ?)",
            (clean["title"], clean["amount"], clean["category"], clean["date"]),
        )
        new_id = cursor.lastrowid
    return jsonify({"id": new_id, "message": "Expense added"}), 201


@app.route("/expenses", methods=["GET"])
def list_expenses():
    """List expenses. Optional filters: ?category=Food&month=2026-11"""
    query = "SELECT * FROM expenses WHERE 1=1"
    params = []
    category = request.args.get("category")
    month = request.args.get("month")  # format YYYY-MM
    if category:
        query += " AND category = ?"
        params.append(category)
    if month:
        query += " AND substr(date, 1, 7) = ?"
        params.append(month)
    query += " ORDER BY date DESC, id DESC"
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return jsonify([dict(row) for row in rows])


@app.route("/expenses/<int:expense_id>", methods=["GET"])
def get_expense(expense_id):
    """Get one expense by id."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM expenses WHERE id = ?", (expense_id,)
        ).fetchone()
    if row is None:
        return jsonify({"error": "Expense not found"}), 404
    return jsonify(dict(row))


@app.route("/expenses/<int:expense_id>", methods=["PUT"])
def update_expense(expense_id):
    """Replace all fields of an expense."""
    clean, error = validate(request.get_json(silent=True) or {})
    if error:
        return jsonify({"error": error}), 400
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE expenses SET title = ?, amount = ?, category = ?, date = ? WHERE id = ?",
            (clean["title"], clean["amount"], clean["category"], clean["date"], expense_id),
        )
    if cursor.rowcount == 0:
        return jsonify({"error": "Expense not found"}), 404
    return jsonify({"message": "Expense updated"})


@app.route("/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    """Delete an expense."""
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    if cursor.rowcount == 0:
        return jsonify({"error": "Expense not found"}), 404
    return jsonify({"message": "Expense deleted"})


@app.route("/summary", methods=["GET"])
def summary():
    """Total spent, overall and per category. Optional filter: ?month=2026-11"""
    month = request.args.get("month")
    where, params = "", []
    if month:
        where = "WHERE substr(date, 1, 7) = ?"
        params.append(month)
    with get_connection() as conn:
        total = conn.execute(
            f"SELECT COALESCE(SUM(amount), 0) AS total, COUNT(*) AS count FROM expenses {where}",
            params,
        ).fetchone()
        rows = conn.execute(
            f"SELECT category, SUM(amount) AS total FROM expenses {where} "
            "GROUP BY category ORDER BY total DESC",
            params,
        ).fetchall()
    return jsonify(
        {
            "month": month or "all",
            "total_spent": round(total["total"], 2),
            "expense_count": total["count"],
            "by_category": {r["category"]: round(r["total"], 2) for r in rows},
        }
    )


init_db()  # make sure the table exists whenever the app starts

if __name__ == "__main__":
    app.run(debug=True)
