# Handle all calendar functions
from utils import format_date, format_time
from datetime import datetime
from database import sqlite_connection

def get_calendar_events(month, year):
    cursor = sqlite_connection.cursor()
    # Sort events by month and year and save title and time(if saved)
    events = cursor.execute(
        "SELECT title, due_datetime, details, category, priority from TASKS WHERE intent='Event' AND completed=0 AND due_datetime LIKE ? ORDER BY due_datetime ASC",
        (f"%{year}-{month:02d}%",)
    ).fetchall()

    dict_events = {}
    for event in events:
        dt = datetime.fromisoformat(event[1])
        day = dt.day

        dict_events.setdefault(day, [])
        dict_events[day].append({
            "title": event[0],
            "time": format_time(event[1]),
            "date": format_date(event[1]),
            "details": event[2] if event[2] else "",
            "category": event[3] if event[3] else "",
            "priority": event[4] if event[4] else ""
        })

    return dict_events