# Nexus – AI Productivity Dashboard

Nexus is a conversational AI productivity dashboard that combines natural language understanding with structured task management. Users can chat naturally with the assistant, and Nexus extracts **Todos**, **Deadlines** and **Goals**, stores them persistently in SQLite, and uses recent conversation history to provide context-aware responses.

Built using **Flask**, **JavaScript**, **HTML/CSS**, and the **Google Gemini API**.

---

## Features

* 💬 Conversational AI assistant powered by Google Gemini
* 🧠 AI-powered intent classification into:
  * Todo
  * Deadline
  * Goal
  * Chat
* ✨ Multi-task extraction from a single message
* 🧩 Context-aware conversations with persistent memory and dashboard state
* 📅 Automatic extraction and normalization of dates and times
* 📋 Live dashboard updates without refreshing the page
* 📝 Persistent task storage using SQLite
* 📖 Conversation history with previous interactions
* ✅ Interactive checkboxes for tracking completed tasks
* 🎨 Clean, responsive dark-themed interface

---

## Tech Stack

* Python
* Flask
* SQLite
* HTML5
* CSS3
* JavaScript (Fetch API)
* Google Gemini API (`google-genai`)

---

## Project Structure

```
Nexus/
│
├── static/
│   ├── css/
│   │   ├── style.css
│   │   └── history.css
│   └── js/
│       └── chat.js
│
├── templates/
│   ├── index.html  
│   └── history.html  
│
├── data/
│   └── dashboard_history.db  
│ 
├── images/
│   ├── dashboard.png 
│   └── history.png 
│
├── app.py  
├── requirements.txt
├── .env
└── README.md
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/aparajaya18-star/Nexus.git
cd Nexus
```

### 2. Create a virtual environment (recommended)

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Gemini API

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

Replace `your_api_key_here` with your Google Gemini API key.

### 5. Run the application

```bash
python app.py
```

Open your browser and visit:

```
http://127.0.0.1:5000
```
> **Note:** The SQLite database is created automatically on first launch.

---

## How It Works

1. The user sends a natural language message.
2. Gemini extracts one or more structured tasks and classifies each as a Todo, Deadline, Goal, or Chat.
3. Relative dates and times are normalized into a standard format.
4. Tasks are stored in a persistent SQLite database.
5. The dashboard updates instantly without refreshing.
6. The assistant generates a context-aware response using the current dashboard state and recent conversation history.
7. The interaction is saved for future conversations.

---

## Demo

A demonstration video is available here:

**https://drive.google.com/drive/folders/1KR7mVJL-LHSxrXoq87u-wBLugBQctHMM?usp=sharing**

---

## Screenshots

### Dashboard

![Dashboard](images/dashboard.png)

### Conversation History

![History](images/history.png)

---

## Future Improvements

* Calendar integration
* Smart reminders and notifications
* Natural language task editing
* Task deletion through chat
* Dashboard analytics and productivity insights
* AI-powered daily planning
* Streaming AI responses
* Function / tool calling
* User authentication

---

## Requirements

```
Flask
google-genai
python-dotenv
Markdown
dateparser
```

---

## Author

**Aparajaya**