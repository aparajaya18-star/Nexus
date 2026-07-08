# -------- Database Setup --------
import sqlite3

# Initialize SQLite database
sqlite_connection = sqlite3.connect('data/dashboard_history.db', check_same_thread=False)
# Create a cursor object to interact with the database
cursor = sqlite_connection.cursor()

def setup_db():

    # Create tables for history and tasks
    query_chat_history = """
    CREATE TABLE IF NOT EXISTS HISTORY (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_input TEXT NOT NULL,
        response TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
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

    cursor.execute(query_chat_history)
    cursor.execute(query_tasks)

    return cursor, sqlite_connection