from fastmcp import FastMCP
import sqlite3
import os

DB_PATH= os.path.join(os.path.dirname(__file__), "expenses.db")
CATEGORIES_PATH= os.path.join(os.path.dirname(__file__), "categories.json")

mcp=FastMCP(name="ExpenseTracker")


def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
        """)
init_db()
@mcp.tool
def add_expense(date, amount: int, category: str, subcategory="", note=""):
    """Add a new expense to the database."""

    # Fix: extract date if MCP sends a dict
    if isinstance(date, dict):
        # common MCP patterns
        date = date.get("value") or date.get("date")

    if not isinstance(date, str):
        raise ValueError("date must be a string in YYYY-MM-DD format")

    with sqlite3.connect(DB_PATH) as c:
        cursor = c.cursor()
        cursor.execute("""
            INSERT INTO expenses (amount, category, date, subcategory, note)
            VALUES (?, ?, ?, ?, ?)
        """, (amount, category, date, subcategory, note))
        c.commit()

    return "Expense added successfully."

@mcp.tool()
def get_expenses_by_category(category:str):
    """Retrieve all expenses for a given category."""
    with sqlite3.connect(DB_PATH) as c:
        cursor = c.cursor()
        cursor.execute("""
            SELECT id, amount, date, subcategory, note
            FROM expenses
            WHERE category = ?
        """, (category,))
        results = cursor.fetchall()
    return results

@mcp.tool()
def list_expenses(start_date=None, end_date=None):
    """List all expenses, optionally filtered by date range."""
    if isinstance(start_date, dict):
        # common MCP patterns
        start_date = start_date.get("value") or start_date.get("date")

    if not isinstance(start_date, str):
        raise ValueError("start_date must be a string in YYYY-MM-DD format")

    if isinstance(end_date, dict):
        # common MCP patterns
        end_date = end_date.get("value") or end_date.get("date")

    if not isinstance(end_date, str):
        raise ValueError("end_date must be a string in YYYY-MM-DD format")
    
    
    with sqlite3.connect(DB_PATH) as c:
        cursor = c.cursor()
        if start_date and end_date:
            cursor.execute("""
                SELECT id, amount, category, date, subcategory, note
                FROM expenses
                WHERE date BETWEEN ? AND ?
            """, (start_date, end_date))
        else:
            cursor.execute("""
                SELECT id, amount, category, date, subcategory, note
                FROM expenses
            """)
        results = cursor.fetchall()
    return results

@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    '''read fresh each time so can be edited without restarting client-server connection'''
    with open(CATEGORIES_PATH, "r",encoding="utf-8") as f:
        return f.read()
    
    
if __name__=="__main__":
    mcp.run(transport="http",host="0.0.0.0",port = 8000)


