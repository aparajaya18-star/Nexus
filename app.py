import markdown
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from flask import Flask, request, render_template, jsonify

load_dotenv()

history = []
model = "gemini-3.1-flash-lite"
from google import genai

client = genai.Client()

CLASSIFIER_SYSTEM_PROMPT = f"""
You are the intent parser for a productivity application.

Analyze the user's message and extract any structured task information.

Classify the message into exactly one of these intents:
- Todo
- Deadline
- Goal
- Chat

Return ONLY valid JSON matching the provided schema.

Rules:
- If the user is adding something they need to do, use "Todo".
- If the user mentions a due date, appointment, exam, meeting, or specific time, use "Deadline".
- If the user describes a long-term aspiration or milestone, use "Goal".
- Otherwise use "Chat".

Extract the following information whenever possible:
- title: a short description of the task or event.
- date: the date exactly as mentioned by the user.
- time: the time exactly as mentioned by the user.

If a field is not present, return null.

Do not invent missing information.
Do not include explanations.
Return JSON only.
"""

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

response_schema = {
    "type": "object",
    "properties": {
        "intent": {
            "type": "string",
            "enum": ["Todo", "Deadline", "Goal", "Chat"]
        },
        "title": {
            "type": ["string", "null"]
        },
        "date": {
            "type": ["string", "null"]
        },
        "time": {
            "type": ["string", "null"]
        },
        "details": {
            "type": ["string", "null"]
        }
    },
    "required": ["intent", "title", "date", "time", "details"]
}

# Function to classify tasks
def classify_message(user_input):
    classification = client.models.generate_content(
    model="gemini-3.1-flash-lite",
    contents=user_input,
    config={
        "system_instruction": CLASSIFIER_SYSTEM_PROMPT,
        "response_mime_type": "application/json",
        "response_json_schema": response_schema
    },
)
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
    classification = {
        "intent": "Chat",
        "title": None,
        "date": None,
        "time": None,
        "details": None
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
                classification = json.loads(classify_message(user_input).text)
                intent = classification["intent"]

                # Get chatbot response
                prompt = f"Chat History: {history}\n\nIntent: {intent}\n\nUser Message: {user_input}"
                response_text = f"{generate_response(prompt)}"
            except Exception as e:
                print(f"ERROR: {e}")
                response_text = "The AI service is temporarily down"
        
        html_output = markdown.markdown(response_text)
        print(html_output)
        # Save input and response in history
        history.append({
        "user": user_input,
        "assistant": response_text,
        "classification": intent
        })

        # Return chat response
        return jsonify({
            "response":html_output,
            "classification": classification
            })
        
    return render_template('index.html', output=html_output, user_input=user_input)    

@app.route('/history')
def history_page():
    return render_template('history.html', history=history)

if __name__ == '__main__':
    app.run(debug=True)
#----APP----