# Building Context
from datetime import datetime
from task_service import get_todos, get_events, get_goals, get_overdue
from history_service import load_history
from utils import format_date, format_time

# Formatting functions for todos, deadlines, goals, and history
def format_todos(todos):
    if not todos:
        return "No todos at the moment."
    return "\n".join([f"{todo['title']}" for todo in todos])

def format_events(events):
    if not events:
        return "No upcoming events."
    
    lines = []

    for event in events:
        lines.append(
            f"- {event['title']} - {format_date(event['due_datetime'])} at {format_time(event['due_datetime'])}"
        )

    return "\n".join(lines)

def format_goals(goals):
    if not goals:
        return "No goals set."
    return "\n".join([f"- {goal['title']}" for goal in goals])

def format_history(history):
    if not history:
        return "No recent conversation."
    return "\n".join([f"User: {item['user_input']}\nBot: {item['response']}" for item in history])

# Function to build context for the chatbot response
def build_context():
    todos = [t for t in get_todos() if not t["completed"]]
    events = [e for e in get_events() if e["due_datetime"] and not e["completed"]]
    goals = get_goals()
    history = load_history(limit=10)

    context = f"""
Current Dashboard

Todos:
{format_todos(todos)}

Upcoming Events:
{format_events(events)}

Goals:
{format_goals(goals)}

Recent Conversation:
{format_history(history)}
"""

    return context