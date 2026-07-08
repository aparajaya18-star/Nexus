# Handle all chat functionalities
from ai import classify_message, generate_response
from context import build_context

def get_chat_response(user_input):
    if not user_input.strip():
        response_text = "There is no input. Please enter something."
    else:
        classified_tasks = { "tasks": []}
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
        
    return response_text, classified_tasks