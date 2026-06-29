import markdown
import json
import dateparser
from datetime import datetime
from google import genai
from google.genai import types
from dotenv import load_dotenv
from flask import Flask, request, render_template, jsonify
from dateparser import parse

load_dotenv()

model = "gemini-3.1-flash-lite"
client = genai.Client()

history = []

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

#----APP----
app = Flask(__name__)
@app.route('/', methods=['GET','POST'])

def home():
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
                prompt = f"Chat History: {history}\n\nDetected Tasks: {classified_tasks['tasks']}\n\nUser Message: {user_input}"
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
        history.append({
            "user_input": user_input,
            "response": html_output,
            "tasks": classified_tasks["tasks"]
        })

        # Return chat response
        return jsonify({
            "response":html_output,
            "classification": classified_tasks
            })
        
    return render_template('index.html', output=html_output, user_input=user_input)    

@app.route('/history')
def history_page():

    stats = {
        "conversations": len(history),
        "todos": 0,
        "deadlines": 0,
        "goals": 0
    }

    for conversation in history:
        for task in conversation["tasks"]:
            if task["intent"] == "Todo":
                stats["todos"] += 1
            elif task["intent"] == "Deadline":
                stats["deadlines"] += 1
            elif task["intent"] == "Goal":
                stats["goals"] += 1

    return render_template('history.html', history=history, stats=stats)

if __name__ == '__main__':
    app.run(debug=True)
#----APP----