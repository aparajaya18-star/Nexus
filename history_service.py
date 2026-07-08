# Handle all history functions
import sqlite3
from database import cursor, sqlite_connection

# Function to retrieve history from the database
def load_history(limit=None):
    query = """
        SELECT id, user_input, response
        FROM HISTORY
        ORDER BY timestamp DESC
    """

    if limit is not None:
        query += " LIMIT ?"
        cursor.execute(query, (limit,))
    else:
        cursor.execute(query)

    history = []

    for history_id, user_input, response in cursor.fetchall():

        cursor.execute("""
            SELECT intent, title, due_datetime, details, category, priority
            FROM TASKS
            WHERE history_id = ?
        """, (history_id,))

        tasks = [
            {
                "intent": intent,
                "title": title,
                "due_datetime": due_datetime,
                "details": details,
                "category": category,
                "priority": priority
            }
            for intent, title, due_datetime, details, category, priority
            in cursor.fetchall()
        ]

        history.append({
            "user_input": user_input,
            "response": response,
            "tasks": tasks
        })

    return history

def save_history(user_input, html_output, classified_tasks):
    cursor.execute(
        "INSERT INTO HISTORY (user_input, response) VALUES (?, ?)",
        (user_input, html_output)
    )
    history_id = cursor.lastrowid
    for task in classified_tasks["tasks"]:
        cursor.execute(
            "INSERT INTO TASKS (history_id, intent, title, due_datetime, priority, category, details) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                history_id,
                task["intent"],
                task.get("title"),
                task.get("due_datetime"),
                task.get("priority"),
                task.get("category"),
                task.get("details")
            )
        )
        task["id"] = cursor.lastrowid  # Store the task ID for later use
    sqlite_connection.commit()