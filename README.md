# Expense Tracker API

A REST API for tracking personal expenses, built with **Python, Flask and SQLite**.
It supports creating, reading, updating and deleting expenses, filtering them by
category and month, and getting a spending summary.

## Features
- Full CRUD for expenses (create, read, update, delete)
- Input validation with clear error messages and HTTP status codes
- Filter by category and month
- Summary endpoint with total spent and totals per category
- SQLite database, no extra setup needed
- Unit tests for the main endpoints

## Tech stack
Python 3, Flask, SQLite (`sqlite3`), `unittest`

## Setup
```bash
git clone https://github.com/Dinesh-mareddy/expense-tracker-api.git
cd expense-tracker-api
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
The API runs at `http://127.0.0.1:5000`.

## Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Check that the API is running |
| POST | `/expenses` | Add an expense |
| GET | `/expenses` | List expenses (optional `?category=Food&month=2026-11`) |
| GET | `/expenses/<id>` | Get one expense |
| PUT | `/expenses/<id>` | Update an expense |
| DELETE | `/expenses/<id>` | Delete an expense |
| GET | `/summary` | Total and per-category totals (optional `?month=2026-11`) |

## Example requests
Add an expense:
```bash
curl -X POST http://127.0.0.1:5000/expenses \
  -H "Content-Type: application/json" \
  -d '{"title":"Lunch","amount":120.5,"category":"Food","date":"2026-11-06"}'
```
Response: `{"id": 1, "message": "Expense added"}`

Get the monthly summary:
```bash
curl "http://127.0.0.1:5000/summary?month=2026-11"
```
Response:
```json
{
  "month": "2026-11",
  "total_spent": 120.5,
  "expense_count": 1,
  "by_category": {"Food": 120.5}
}
```

## Running the tests
```bash
python -m unittest
```

## Project structure
```
expense-tracker-api/
├── app.py            # Flask app and routes
├── test_app.py       # Unit tests
├── requirements.txt
└── README.md
```

## Possible improvements
- User login and authentication
- Pagination for large expense lists
- Deployment to a cloud platform

## Author
Dinesh Kumar Reddy Mareddy
