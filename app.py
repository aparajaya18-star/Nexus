import markdown
from dotenv import load_dotenv
from flask import Flask, request, render_template, jsonify

# Import functions from different files
from config import configure
from database import setup_db
from task_service import get_todos, get_events, get_goals, get_overdue
from history_service import load_history, save_history
from calendar_service import get_calendar_events
from chat import get_chat_response
from budget_service import (
    get_budget_summary,
    set_monthly_budget,
    add_expense,
    delete_expense
)


load_dotenv()

model, client, CLASSIFIER_SYSTEM_PROMPT, RESPONSE_SCHEMA, CHATBOT_SYSTEM_PROMPT = configure()
cursor, sqlite_connection = setup_db()

# ----APP----
app = Flask(__name__)

# Home route to render the main page with tasks
@app.route('/')
def home():
    return render_template('index.html')  

# Chat route to handle user input and generate responses
@app.route("/chat", methods=["POST"])
def chat():
    response_text=""
    user_input=""
    html_output=""

    if request.method == 'POST':
        # Get user input
        data = request.get_json()
        user_input = data['message'][0]['content']

        # Get chat response
        response_text, classified_tasks = get_chat_response(user_input)
        html_output = markdown.markdown(response_text)
        print(html_output)

        # Save input and response in history
        save_history(user_input, html_output, classified_tasks)      

        # Return chat response
        return jsonify({
            "response":html_output,
            "classification": classified_tasks
            })
    
# Route to handle tasks
@app.route("/task", methods=["GET"])
def handle_task():
    return jsonify({
        "todos": get_todos(),
        "events": get_events(),
        "goals": get_goals(),
        "overdue": get_overdue()
    }
    )
    
@app.route("/update_task", methods=["POST"] )
def update_task():
    # Update Tasks
    data = request.get_json()
    print(data)

    cursor.execute(
        "UPDATE TASKS SET completed=? WHERE id=?",
        (data["completed"], data["id"])
    )

    sqlite_connection.commit()

    cursor.execute(
        "SELECT id, completed, typeof(completed) FROM TASKS WHERE id=?",
        (data["id"],)
    )
    print(cursor.fetchone())

    return jsonify(success=True)

# Route to send events to Calendar
@app.route("/calendar", methods=["POST"])
def calendar():

    data=request.get_json()

    return jsonify(
        get_calendar_events(
            data["month"],
            data["year"]
        )
    )

# Route to render the history page with statistics
@app.route('/history')
def history_page():

    stats = {
        "conversations": 0,
        "todos": 0,
        "events": 0,
        "goals": 0
    }

    stats["conversations"] = cursor.execute("SELECT COUNT(*) FROM HISTORY").fetchone()[0]
    stats["todos"] = cursor.execute("SELECT COUNT(*) FROM TASKS WHERE intent='Todo'").fetchone()[0]
    stats["events"] = cursor.execute("SELECT COUNT(*) FROM TASKS WHERE intent='Event'").fetchone()[0]
    stats["goals"] = cursor.execute("SELECT COUNT(*) FROM TASKS WHERE intent='Goal'").fetchone()[0]

    history = load_history()

    return render_template('history.html', history=history, stats=stats)

@app.route('/analytics')
def analytics_page():
    return render_template('analytics.html')

@app.route('/settings')
def settings_page():
    return render_template('settings.html')

# -------- Budget API --------

@app.route("/budget/data", methods=["GET"])
def budget_data():
    return jsonify(get_budget_summary())


@app.route("/budget", methods=["POST"])
def update_budget():
    data = request.get_json()

    amount = float(data["amount"])

    if amount <= 0:
        return jsonify({
            "error": "Budget must be greater than zero."
        }), 400

    set_monthly_budget(amount)

    return jsonify(success=True)


@app.route("/budget/expense", methods=["POST"])
def create_expense():
    data = request.get_json()

    description = data["description"].strip()
    amount = float(data["amount"])
    category = data["category"]
    expense_date = data["date"]

    if not description or amount <= 0 or not expense_date:
        return jsonify({
            "error": "Invalid expense data."
        }), 400

    expense_id = add_expense(
        description,
        amount,
        category,
        expense_date
    )

    return jsonify({
        "success": True,
        "id": expense_id
    })


@app.route("/budget/expense/<int:expense_id>", methods=["DELETE"])
def remove_expense(expense_id):
    delete_expense(expense_id)

    return jsonify(success=True)

@app.route('/budget')
def budget_page():
    return render_template('budget.html')

if __name__ == '__main__':
    app.run(debug=True)
#----APP----