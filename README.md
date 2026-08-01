# Smart Expense Tracker API

A REST API to manage personal expenses. Built with Python and Flask, with data
stored in a local JSON file (no database required).

Supports:
- Adding an expense (`id`, `title`, `amount`, `category`, `date`)
- Viewing all expenses
- Filtering expenses by category
- Deleting an expense
- Bonus: a monthly summary endpoint (`GET /api/expenses/summary/monthly`)

## Install

```
pip install -r requirements.txt
```

## Run the server

```
python src/app.py
```

Server runs at `http://127.0.0.1:5000`.

## Run the tests

```
pytest tests/
```
