# Handle all tasks
import re
from database import sqlite_connection
from utils import format_date, format_time

cursor = sqlite_connection.cursor()

def serialize_task(row):
    return {
                "id": row[0],
                "intent": row[1],
                "title": row[2],
                "due_datetime": row[3] or "",
                "date": format_date(row[3]) or "",
                "time": format_time(row[3]) or "",
                "details": row[4] or "",
                "category": row[5] or "",
                "priority": row[6] or "",
                "completed": row[7]
            }
                

def get_todos():
    cursor.execute("""
        SELECT id, intent, title, due_datetime, details, category, priority, completed
        FROM TASKS
        WHERE intent = "Todo"
        AND created_at >= datetime('now', '-7 days')
        ORDER BY completed ASC, created_at DESC
    """)
    return [serialize_task(row) for row in cursor.fetchall()]

def get_events():
    cursor.execute("""
        SELECT id, intent, title, due_datetime, details, category, priority, completed
        FROM TASKS
        WHERE intent = "Event"
        AND due_datetime >= datetime('now')
        ORDER BY completed ASC, created_at DESC
    """)
    return [serialize_task(row) for row in cursor.fetchall()]

def get_goals():
    cursor.execute("""
        SELECT id, intent, title, due_datetime, details, category, priority, completed
        FROM TASKS
        WHERE intent = "Goal"
        ORDER BY completed ASC, created_at DESC
    """ )

    return [serialize_task(row) for row in cursor.fetchall()]

def get_overdue():

    # Sorting overdue tasks
    cursor.execute("""
        SELECT id, intent, title, due_datetime, details, category, priority, completed
        FROM TASKS
        WHERE intent = "Todo"
        AND completed = 0
        AND created_at < datetime('now', '-7 days')
        ORDER BY completed ASC, created_at DESC
    """)
    overdue_todos = [serialize_task(row) for row in cursor.fetchall()]

    # Sorting overdue events
    cursor.execute("""
        SELECT id, intent, title, due_datetime, details, category, priority, completed
        FROM TASKS
        WHERE intent = "Event"
        AND completed = 0
        AND due_datetime IS NOT NULL
        AND due_datetime < datetime('now')
        ORDER BY completed ASC, created_at DESC
    """)
    overdue_events = [serialize_task(row) for row in cursor.fetchall()]
    
    overdue_events.extend(overdue_todos)
    return overdue_events
