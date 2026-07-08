# Manage all connections with the ai api
from config import CLASSIFIER_SYSTEM_PROMPT, RESPONSE_SCHEMA, CHATBOT_SYSTEM_PROMPT, client, model
from datetime import datetime
import dateparser
import json

# Function to classify tasks
def classify_message(user_input):
    response = client.models.generate_content(
        model=model,
        contents=user_input,
        config={
            "system_instruction": CLASSIFIER_SYSTEM_PROMPT,
            "response_mime_type": "application/json",
            "response_json_schema": RESPONSE_SCHEMA
        }
    )

    classification = json.loads(response.text)

    print(f"Classification: {classification}")
    
    for task in classification["tasks"]:
        normalize_datetime(task)

    return classification

# Function to normalize datetime
def normalize_datetime(classification):
    if classification["due_datetime"]:
        parsed = dateparser.parse(classification["due_datetime"],
                                  settings={
                                      "RELATIVE_BASE": datetime.now(),
                                      "PREFER_DATES_FROM": "future",
                                  })
        if parsed:
            classification["due_datetime"] = parsed.isoformat()
        else:
            classification["due_datetime"] = None
    return classification

# Function to generate response
def generate_response(prompt, temp=0.5):
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
        "system_instruction": CHATBOT_SYSTEM_PROMPT,
        "temperature":temp
        }
    )
    # Add streaming convos later
    return response.text