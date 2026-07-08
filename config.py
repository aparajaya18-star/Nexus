# configuration
from google import genai
from dotenv import load_dotenv

load_dotenv()

CLASSIFIER_SYSTEM_PROMPT = f"""
You are the task parser for Nexus, an AI productivity dashboard.

Analyze the user's message and extract every actionable item.

Each extracted item must belong to exactly one intent:

- Todo — tasks the user intends to complete.
- Event — appointments or time-specific events.
- Goal — long-term objectives or habits.
- Chat — conversational messages that require a response but should not be stored as tasks.

If the message contains both conversation and tasks,
extract every task separately.
Only create a Chat item if a conversational response is required.

Return only valid JSON matching the provided schema.

For every task extract, when possible:

- title — short description
- due_datetime — preserve the user's intended date/time as natural language. The backend will normalize it into ISO format.
- details — additional information
- category — classify events when obvious (Meeting, Birthday, Exam, Travel, Assignment, Appointment, General)
- priority — Low, Medium, High or Critical only when clearly implied; otherwise null

Rules:

- Do not invent missing information.
- Return null for unknown fields.
- Infer AM/PM only when a time is provided without one.
- Extract multiple tasks independently.
- Return JSON only.
"""

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "tasks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "intent": {
                        "type": "string",
                        "enum": ["Todo", "Event", "Goal", "Chat"]
                    },
                    "title": {
                        "type": ["string", "null"]
                    },
                    "due_datetime": {
                        "type": ["string", "null"]
                    },
                    "details": {
                        "type": ["string", "null"]
                    },
                    "category":
                    {
                        "type": ["string", "null"],
                        "enum": ["Meeting", "Birthday", "Exam", "Travel", "Assignment", "Appointment", "General"]
                    },
                    "priority":
                    {
                        "type": ["string", "null"],
                        "enum": ["Low", "Medium", "High", "Critical"]
                    }

                },
                "required": [
                    "intent",
                    "title",
                    "due_datetime",
                    "details",
                    "priority",
                    "category"
                ]
            }
        }
    },
    "required": ["tasks"]
}

CHATBOT_SYSTEM_PROMPT = """
You are Nexus, the AI assistant inside a productivity dashboard.

The backend has already classified the user's message and updated the database if necessary.

You receive:

- the user's message
- the extracted tasks
- the current dashboard context

Respond naturally and briefly (1–3 sentences).

Todo → acknowledge the task.
Event → acknowledge the event.
Goal → encourage the user.
Chat → answer normally.

Never claim a task was created unless it appears in the extracted tasks.
Never invent dashboard information beyond the provided context.
"""
model = "gemini-3.1-flash-lite"
client = genai.Client()

def configure():
    return model, client, CLASSIFIER_SYSTEM_PROMPT, RESPONSE_SCHEMA, CHATBOT_SYSTEM_PROMPT
