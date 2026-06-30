import markdown
import json
import dateparser
import sqlite3
from datetime import datetime
from google import genai
from google.genai import types
from dotenv import load_dotenv
from flask import Flask, request, render_template, jsonify
from dateparser import parse

load_dotenv()

# -------- Configuration --------
model = "gemini-3.1-flash-lite"
client = genai.Client()

CLASSIFIER_SYSTEM_PROMPT = f"""
You are the intent parser for a productivity application.

Analyze the user's message and extract any structured task information.
A single message may contain zero, one, or multiple tasks. 
Extract every distinct task separately. 

Classify each task into exactly one of these intents:
- Todo
- Deadline
- Goal
- Chat

If a message contains both conversational text and tasks, include a Chat item for the conversational portion only if it requires a response; otherwise only return the extracted tasks.

Return ONLY valid JSON matching the provided schema.

Rules:
- If the user is adding something they need to do, use "Todo".
- If the user mentions a due date, appointment, exam, meeting, or specific time, use "Deadline".
- If the user describes a long-term aspiration or milestone, use "Goal".
- Otherwise use "Chat".

Extract the following information whenever possible:
- title: a short description of the task or event.
- datetime: Extract a single datetime field.

If the user specifies a time without AM or PM,
infer the most likely interpretation from context and always return
the time with AM or PM included.

Examples:

"I have a test tomorrow at 9"
→ "tomorrow at 9 AM"

"I have dinner tomorrow at 9"
→ "tomorrow at 9 PM"

"I have class Monday at 8"
→ "Monday at 8 AM"

"My flight leaves at 11"
→ "today at 11 AM"

Always include AM or PM whenever a time is present.

If a field is not present, return null.

Do not invent missing information.
Do not include explanations.
Return JSON only.
"""

response_schema = {
    "type": "object",
    "properties": {
        "tasks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "intent": {
                        "type": "string",
                        "enum": ["Todo", "Deadline", "Goal", "Chat"]
                    },
                    "title": {
                        "type": ["string", "null"]
                    },
                    "datetime": {
                        "type": ["string", "null"]
                    },
                    "details": {
                        "type": ["string", "null"]
                    }
                },
                "required": [
                    "intent",
                    "title",
                    "datetime",
                    "details"
                ]
            }
        }
    },
    "required": ["tasks"]
}

chatbot_system_prompt = """
You are Nexus, the AI assistant inside a productivity dashboard.

Your job is to help users stay organized.

The backend has already classified the user's message and updated the appropriate list if necessary.

You will receive:
- the user's message
- the detected intent

Respond naturally and conversationally.

If the intent is:
- Todo: acknowledge that the task has been added.
- Deadline: acknowledge the deadline and encourage the user.
- Goal: congratulate them on setting a goal and offer help if appropriate.
- Chat: simply answer normally.

Never invent tasks or claim something was added unless the classification indicates it.

Keep responses concise (1-3 sentences).
"""

# -------- Database Setup --------

# Initialize SQLite database
sqlite_connection = sqlite3.connect('data/dashboard_history.db', check_same_thread=False)
# Create a cursor object to interact with the database
cursor = sqlite_connection.cursor()

# Create tables for history and tasks
query_history = """
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
    datetime TEXT,
    date TEXT,
    time TEXT,
    details TEXT,
    completed BOOLEAN DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (history_id) REFERENCES HISTORY(id)
)
"""

cursor.execute(query_history)
cursor.execute(query_tasks)

# -------- Functions --------

# Function to classify tasks
def classify_message(user_input):
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=user_input,
        config={
            "system_instruction": CLASSIFIER_SYSTEM_PROMPT,
            "response_mime_type": "application/json",
            "response_json_schema": response_schema
        }
    )

    classification = json.loads(response.text)

    print(f"Classification: {classification}")
    
    for task in classification["tasks"]:
        normalize_datetime(task)

    return classification

# Function to normalize datetime
def normalize_datetime(classification):
    if classification["datetime"]:
        parsed = dateparser.parse(classification["datetime"],
                                  settings={
                                      "RELATIVE_BASE": datetime.now(),
                                      "PREFER_DATES_FROM": "future",
                                  })
        if parsed:
            classification["datetime"] = parsed.isoformat()
            classification["date"] = parsed.strftime("%d %b %Y")
            classification["time"] = parsed.strftime("%I:%M %p")
        else:
            classification["datetime"] = None
            classification["date"] = None
            classification["time"] = None
    return classification

# Function to generate response
def generate_response(prompt, temp=0.5):
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
        config={
        "system_instruction": chatbot_system_prompt,
        "temperature":temp
        }
    )
    # Add streaming convos later
    return response.text

# Functions to retrieve tasks by intent
def get_tasks_by_intent(intent_name):
    cursor.execute("""
        SELECT id, title, date, time, details, completed
        FROM TASKS
        WHERE intent = ?
        ORDER BY completed ASC, timestamp DESC
    """, (intent_name,))
    tasks = [
            {
                "id": task_id,
                "intent": intent_name,
                "title": title,
                "date": date,
                "time": time,
                "details": details,
                "completed": completed
            }
            for task_id, title, date, time, details, completed
            in cursor.fetchall()
        ]
    return tasks

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
            SELECT intent, title, date, time, details
            FROM TASKS
            WHERE history_id = ?
        """, (history_id,))

        tasks = [
            {
                "intent": intent,
                "title": title,
                "date": date,
                "time": time,
                "details": details
            }
            for intent, title, date, time, details
            in cursor.fetchall()
        ]

        history.append({
            "user_input": user_input,
            "response": response,
            "tasks": tasks
        })

    return history

# Formatting functions for todos, deadlines, goals, and history
def format_todos(todos):
    if not todos:
        return "No todos at the moment."
    return "\n".join([f"{todo['title']}" for todo in todos])

def format_deadlines(deadlines):
    if not deadlines:
        return "No upcoming deadlines."
    return "\n".join([f"- {deadline['title']} - {deadline['date']} at {deadline['time']}" for deadline in deadlines])

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
    todos = [t for t in get_tasks_by_intent("Todo") if not t["completed"]]
    deadlines = [d for d in get_tasks_by_intent("Deadline") if d["date"] and d["time"] and not d["completed"]]
    goals = get_tasks_by_intent("Goal")
    history = load_history(limit=10)

    context = f"""
Current Dashboard

Todos:
{format_todos(todos)}

Upcoming Deadlines:
{format_deadlines(deadlines)}

Goals:
{format_goals(goals)}

Recent Conversation:
{format_history(history)}
"""

    return context

# ----APP----
app = Flask(__name__)

# Home route to render the main page with tasks
@app.route('/', methods=['GET','POST'])
def home():
    return render_template('index.html', todos=get_tasks_by_intent('Todo'), deadlines=get_tasks_by_intent('Deadline'), goals=get_tasks_by_intent('Goal'))  

# Chat route to handle user input and generate responses
@app.route("/chat", methods=["POST"])
def chat():
    response_text=""
    user_input=""
    html_output=""
    intent = "Chat"
    classified_tasks = {
        "tasks": [
            {
                "intent": intent,
                "title": None,
                "datetime": None,
                "date": None,
                "time": None,
                "details": None
            }
        ]
    }

    if request.method == 'POST':
        # Get user input
        data = request.get_json()
        user_input = data['message'][0]['content']

        # Check for valid user input
        if not user_input.strip():
            response_text = "There is no input. Please enter something."
        else:
            try:
                # Get Classification
                classified_tasks = classify_message(user_input)

                # Get chatbot response
                context = build_context()
                prompt = f"Current User Message: {user_input}\n\nDetected Tasks: {classified_tasks['tasks']}\n\n{context}"
                response_text = f"{generate_response(prompt)}"
            except Exception as e:
                print(e)

                for task in classified_tasks["tasks"]:
                    if task["intent"] != "Chat":
                        response_text = (
                            "I've added that to your dashboard, "
                            "but I'm having trouble generating a reply right now."
                        )
                    else:
                        response_text = (
                            "I'm having trouble reaching Gemini at the moment."
                        )
        
        html_output = markdown.markdown(response_text)
        print(html_output)
        # Save input and response in history
        cursor.execute(
            "INSERT INTO HISTORY (user_input, response) VALUES (?, ?)",
            (user_input, html_output)
        )
        history_id = cursor.lastrowid
        for task in classified_tasks["tasks"]:
            cursor.execute(
                "INSERT INTO TASKS (history_id, intent, title, datetime, date, time, details) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    history_id,
                    task["intent"],
                    task.get("title"),
                    task.get("datetime"),
                    task.get("date"),
                    task.get("time"),
                    task.get("details")
                )
            )
            task["id"] = cursor.lastrowid  # Store the task ID for later use
        sqlite_connection.commit()      

        # Return chat response
        return jsonify({
            "response":html_output,
            "classification": classified_tasks
            })
    
# Route to update task completion status
@app.route("/update_task", methods=["POST"])
def update_task():
    data = request.get_json()

    cursor.execute(
        "UPDATE TASKS SET completed=? WHERE id=?",
        (data["completed"], data["id"])
    )

    sqlite_connection.commit()

    return jsonify(success=True)

# Route to render the history page with statistics
@app.route('/history')
def history_page():

    stats = {
        "conversations": 0,
        "todos": 0,
        "deadlines": 0,
        "goals": 0
    }

    stats["conversations"] = cursor.execute("SELECT COUNT(*) FROM HISTORY").fetchone()[0]
    stats["todos"] = cursor.execute("SELECT COUNT(*) FROM TASKS WHERE intent='Todo'").fetchone()[0]
    stats["deadlines"] = cursor.execute("SELECT COUNT(*) FROM TASKS WHERE intent='Deadline'").fetchone()[0]
    stats["goals"] = cursor.execute("SELECT COUNT(*) FROM TASKS WHERE intent='Goal'").fetchone()[0]

    history = load_history()

    return render_template('history.html', history=history, stats=stats)

if __name__ == '__main__':
    app.run(debug=True)
#----APP----