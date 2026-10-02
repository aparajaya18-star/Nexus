# -------- Database Setup --------
import sqlite3

# Initialize SQLite database
sqlite_connection = sqlite3.connect(
    'data/dashboard_history.db',
    check_same_thread=False
)

cursor = sqlite_connection.cursor()


def setup_db():

    # Chat history
    query_chat_history = """
    CREATE TABLE IF NOT EXISTS HISTORY (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_input TEXT NOT NULL,
        response TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """

    # Tasks
    query_tasks = """
    CREATE TABLE IF NOT EXISTS TASKS (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        history_id INTEGER NOT NULL,
        intent TEXT NOT NULL,
        title TEXT,
        details TEXT,
        due_datetime TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME,
        completed_at DATETIME,
        completed BOOLEAN DEFAULT 0,
        priority TEXT,
        category TEXT,
        status TEXT,
        FOREIGN KEY (history_id) REFERENCES HISTORY(id)
    )
    """

    # Monthly budgets
    query_budgets = """
    CREATE TABLE IF NOT EXISTS BUDGETS (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        month INTEGER NOT NULL,
        year INTEGER NOT NULL,
        amount REAL NOT NULL,
        UNIQUE(month, year)
    )
    """

    # Expenses
    query_expenses = """
    CREATE TABLE IF NOT EXISTS EXPENSES (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        expense_date TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """

    cursor.execute(query_chat_history)
    cursor.execute(query_tasks)
    cursor.execute(query_budgets)
    cursor.execute(query_expenses)

    sqlite_connection.commit()

    return cursor, sqlite_connection