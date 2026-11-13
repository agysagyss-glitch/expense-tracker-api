from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI(title="Expense Tracker API")

# 1. Initialize SQLite Database
def init_db():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# 2. Data Validation Schema
class Expense(BaseModel):
    title: str
    amount: float
    category: str

# 3. API Endpoints (Create, Read, Delete)
@app.post("/expenses/", status_code=201)
def add_expense(expense: Expense):
    if expense.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (title, amount, category) VALUES (?, ?, ?)",
        (expense.title, expense.amount, expense.category)
    )
    conn.commit()
    expense_id = cursor.lastrowid
    conn.close()
    return {"id": expense_id, "message": "Expense added successfully", "data": expense}

@app.get("/expenses/")
def get_all_expenses():
    conn = sqlite3.connect("expenses.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"total_items": len(rows), "expenses": rows}

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": f"Expense {expense_id} deleted"}
