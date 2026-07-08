# Handle all tasks
from database import cursor

def get_todos():
    cursor.execute("""
        SELECT id, intent, title, due_datetime, details, priority, completed
        FROM TASKS
        WHERE intent = "Todo"
        AND created_at >= datetime('now', '-7 days')
        ORDER BY completed ASC, created_at DESC
    """)
    todos = [
            {
                "id": task_id,
                "intent": intent,
                "title": title,
                "due_datetime": due_datetime,
                "details": details,
                "priority": priority,
                "completed": completed
            }
            for task_id, intent, title, due_datetime, details, priority, completed
            in cursor.fetchall()
        ]
    return todos

def get_events():
    cursor.execute("""
        SELECT id, intent, title, due_datetime, details, category, priority, completed
        FROM TASKS
        WHERE intent = "Event"
        AND due_datetime >= datetime('now')
        ORDER BY completed ASC, created_at DESC
    """)
    events = [
            {
                "id": task_id,
                "intent": intent,
                "title": title,
                "due_datetime": due_datetime,
                "details": details,
                "category": category,
                "priority": priority,
                "completed": completed
            }
            for task_id, intent, title, due_datetime, details, category, priority, completed
            in cursor.fetchall()
        ]
    return events

def get_goals():
    cursor.execute("""
        SELECT id, intent, title, due_datetime, details, priority, completed
        FROM TASKS
        WHERE intent = "Goal"
        ORDER BY completed ASC, created_at DESC
    """ )

    goals = [
            {
            "id": task_id,
                "intent": intent,
                "title": title,
                "due_datetime": due_datetime,
                "details": details,
                "priority": priority,
                "completed": completed
            }
            for task_id, intent, title, due_datetime, details, priority, completed
            in cursor.fetchall()
        ]
    return goals

def get_overdue():

    # Sorting overdue tasks
    cursor.execute("""
        SELECT id, title, due_datetime, details, priority, completed
        FROM TASKS
        WHERE intent = "Todo"
        AND completed = 0
        AND created_at < datetime('now', '-7 days')
        ORDER BY completed ASC, created_at DESC
    """)
    overdue_todos = [
            {
                "id": task_id,
                "intent": "Todo",
                "title": title,
                "due_datetime": due_datetime,
                "details": details,
                "priority": priority,
                "completed": completed
            }
            for task_id, title, due_datetime, details, priority, completed
            in cursor.fetchall()
        ] 

    # Sorting overdue events
    cursor.execute("""
        SELECT id, title, due_datetime, details, priority, completed
        FROM TASKS
        WHERE intent = "Event"
        AND completed = 0
        AND due_datetime IS NOT NULL
        AND due_datetime < datetime('now')
        ORDER BY completed ASC, created_at DESC
    """)
    overdue_events = [
            {
                "id": task_id,
                "intent": "Event",
                "title": title,
                "due_datetime": due_datetime,
                "details": details,
                "priority": priority,
                "completed": completed
            }
            for task_id, title, due_datetime, details, priority, completed
            in cursor.fetchall()
        ] 
    
    overdue_events.extend(overdue_todos)
    return overdue_events
