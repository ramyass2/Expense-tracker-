"""
Test suite for the Smart Expense Tracker API.

Run with: pytest tests/
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest
import app as app_module


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Point the app at a throwaway data file so tests never touch real data
    test_file = tmp_path / "expenses.json"
    monkeypatch.setattr(app_module, "EXPENSES_FILE", test_file)

    flask_app = app_module.create_app()
    flask_app.config.update({"TESTING": True})

    with flask_app.test_client() as c:
        yield c


def test_home(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_add_expense_success(client):
    resp = client.post("/api/expenses", json={
        "title": "Groceries",
        "amount": 450.50,
        "category": "Food",
        "date": "2026-07-15",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["title"] == "Groceries"
    assert data["amount"] == 450.50
    assert data["category"] == "Food"
    assert "id" in data


def test_add_expense_missing_title(client):
    resp = client.post("/api/expenses", json={"amount": 100})
    assert resp.status_code == 400


def test_add_expense_missing_amount(client):
    resp = client.post("/api/expenses", json={"title": "Coffee"})
    assert resp.status_code == 400


def test_add_expense_defaults_category_and_date(client):
    resp = client.post("/api/expenses", json={"title": "Misc", "amount": 20})
    data = resp.get_json()
    assert data["category"] == "General"
    assert data["date"]  # auto-filled with today's date


def test_view_all_expenses(client):
    client.post("/api/expenses", json={"title": "Bus ticket", "amount": 30, "category": "Travel"})
    client.post("/api/expenses", json={"title": "Lunch", "amount": 200, "category": "Food"})

    resp = client.get("/api/expenses")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 2


def test_filter_expenses_by_category(client):
    client.post("/api/expenses", json={"title": "Bus ticket", "amount": 30, "category": "Travel"})
    client.post("/api/expenses", json={"title": "Lunch", "amount": 200, "category": "Food"})
    client.post("/api/expenses", json={"title": "Dinner", "amount": 300, "category": "food"})  # different case

    resp = client.get("/api/expenses?category=Food")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 2  # case-insensitive match
    assert all(e["category"].lower() == "food" for e in data)


def test_filter_expenses_by_category_no_match(client):
    client.post("/api/expenses", json={"title": "Lunch", "amount": 200, "category": "Food"})
    resp = client.get("/api/expenses?category=Rent")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_delete_expense(client):
    add_resp = client.post("/api/expenses", json={"title": "Movie", "amount": 350, "category": "Entertainment"})
    expense_id = add_resp.get_json()["id"]

    del_resp = client.delete(f"/api/expenses/{expense_id}")
    assert del_resp.status_code == 200

    list_resp = client.get("/api/expenses")
    assert list_resp.get_json() == []


def test_delete_nonexistent_expense(client):
    resp = client.delete("/api/expenses/does-not-exist")
    assert resp.status_code == 404


def test_monthly_summary(client):
    client.post("/api/expenses", json={"title": "Rent", "amount": 10000, "category": "Housing", "date": "2026-07-01"})
    client.post("/api/expenses", json={"title": "Groceries", "amount": 1500, "category": "Food", "date": "2026-07-15"})
    client.post("/api/expenses", json={"title": "Old expense", "amount": 500, "category": "Food", "date": "2025-01-01"})

    resp = client.get("/api/expenses/summary/monthly?month=2026-07")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["month"] == "2026-07"
    assert data["count"] == 2
    assert data["total"] == 11500
    assert data["byCategory"]["Housing"] == 10000
    assert data["byCategory"]["Food"] == 1500
