
"""
Smart Expense Tracker API
--------------------------
A small Flask REST API for managing personal expenses.

Endpoints:
    POST   /api/expenses                -> add an expense
    GET    /api/expenses                -> view all expenses
    GET    /api/expenses?category=Food   -> filter expenses by category
    DELETE /api/expenses/<id>           -> delete an expense
    GET    /api/expenses/summary/monthly -> (bonus) monthly summary by category
"""

from flask import Flask, jsonify, request
from pathlib import Path
from datetime import datetime, timezone
import json
import uuid

from storage import read_json, write_json

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
EXPENSES_FILE = DATA_DIR / "expenses.json"


def create_app():
    app = Flask(__name__)

    @app.get("/")
    def home():
        return jsonify({"status": "ok", "service": "Smart Expense Tracker API"})

    @app.post("/api/expenses")
    def add_expense():
        body = request.get_json(silent=True) or {}

        title = body.get("title")
        amount = body.get("amount")

        if not title or not str(title).strip():
            return jsonify({"error": "title is required"}), 400
        if amount is None:
            return jsonify({"error": "amount is required"}), 400
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return jsonify({"error": "amount must be a number"}), 400

        expense = {
            "id": body.get("id") or str(uuid.uuid4()),
            "title": str(title).strip(),
            "amount": amount,
            "category": body.get("category", "General"),
            "date": body.get("date") or datetime.now(timezone.utc).date().isoformat(),
        }

        expenses = read_json(EXPENSES_FILE, [])
        expenses.append(expense)
        write_json(EXPENSES_FILE, expenses)
        return jsonify(expense), 201

    @app.get("/api/expenses")
    def get_expenses():
        expenses = read_json(EXPENSES_FILE, [])

        category = request.args.get("category")
        if category:
            expenses = [
                e for e in expenses
                if str(e.get("category", "")).lower() == category.lower()
            ]

        return jsonify(expenses), 200

    @app.delete("/api/expenses/<expense_id>")
    def delete_expense(expense_id):
        expenses = read_json(EXPENSES_FILE, [])
        remaining = [e for e in expenses if e.get("id") != expense_id]

        if len(remaining) == len(expenses):
            return jsonify({"error": "Expense not found"}), 404

        write_json(EXPENSES_FILE, remaining)
        return jsonify({"message": "Expense deleted", "id": expense_id}), 200

    # ---- Bonus: monthly summary endpoint ----
    @app.get("/api/expenses/summary/monthly")
    def monthly_summary():
        month_param = request.args.get("month")  # optional "YYYY-MM"
        expenses = read_json(EXPENSES_FILE, [])

        if not month_param:
            month_param = datetime.now(timezone.utc).strftime("%Y-%m")

        matched = [e for e in expenses if str(e.get("date", "")).startswith(month_param)]

        by_category = {}
        total = 0.0
        for e in matched:
            amt = float(e.get("amount", 0))
            cat = e.get("category", "General")
            by_category[cat] = by_category.get(cat, 0) + amt
            total += amt

        return jsonify({
            "month": month_param,
            "total": total,
            "count": len(matched),
            "byCategory": by_category,
        }), 200

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
