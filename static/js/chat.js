const chatInput = 
    document.querySelector(".chat-input textarea");
const sendChatBtn =
    document.querySelector(".chat-input button");
const chatbox = document.querySelector('.chatbox')
const url = "/chat";
let userMessage; 

// ----- Rendering Lists Logic -----

async function refreshDashboard(){
    // Get fresh lists from database
    const response = await fetch ("/task",{
            method: "GET",
            headers: {
                "Accept": "application/json"
            }
        });
    const data = await response.json();

    // Clear old list
    clearLists();

    // Add new items to all lists
    renderList("todo",data.todos);
    renderList("event",data.events);
    renderList("goal",data.goals);
    renderList("overdue",data.overdue);
}

function clearLists() {
    document.querySelectorAll(".task-list").forEach(list => {
        list.innerHTML = "";
    });
}

function getHTML(item, list_type)
{
    switch(list_type)
    {
        case "todo":
            return `
            <label class="task-entry">
                <input
                        type="checkbox"
                        class="task-check"
                        data-id="${item.id}"
                        ${item.completed ? "checked" : ""}>
                <span>${item.title}</span>
            </label>
            `;
        case "event":
            return `
                <label class="task-entry">
                    <input
                        type="checkbox"
                        class="task-check"
                        data-id="${item.id}"
                        ${item.completed ? "checked" : ""}>
                    <div>
                        <strong>${item.title}</strong><br>
                        📅 ${item.date ?? "-"}<br>
                        ${item.time ? `<br>🕒 ${item.time}` : ""}
                    </div>
                </label>
            `;
        case "goal":
            return `
                <label class="task-entry">
                    <input
                        type="checkbox"
                        class="task-check"
                        data-id="${item.id}"
                        ${item.completed ? "checked" : ""}>
                    <div>
                        <strong>🎯 ${item.title}</strong>
                        ${item.details ? `<br>${item.details}` : ""}
                    </div>
                </label>
            `;
        case "overdue":
            return `
                <label class="task-entry">
                    <input
                        type="checkbox"
                        class="task-check"
                        data-id="${item.id}"
                        ${item.completed ? "checked" : ""}>
                    <div>
                        <strong>🛑 ${item.title}</strong>
                        ${item.details ? `<br>${item.details}` : ""}
                        ${item.date ? `<br>${item.date}` : ""}
                        ${item.time ? `<br>${item.time}` : ""}
                    </div>
                </label>
            `;
        default:
            throw new Error(`Unknown list type: ${list_type}`);
    }
    
}

function createTaskElement(item, listType) {
    const taskLi = document.createElement("li");
    taskLi.classList.add("task-item");
    taskLi.innerHTML = getHTML(item, listType);

    if (item.completed) {
        taskLi.classList.add("completed");
    }

    const checkbox = taskLi.querySelector(".task-check");
    checkbox.addEventListener("change", () => handleCheckboxChange(checkbox));

    return taskLi;
}

function renderPlaceholder(list, listName) {
    const placeholder_text = {
        "todo": "No tasks today.",
        "event": "No upcoming events.",
        "goal": "No goals.",
        "overdue": "Nothing overdue 🎉"
    }
    const li = document.createElement("li");
    li.classList.add("placeholder");
    li.textContent = placeholder_text[listName];
    list.appendChild(li);
}

function renderList(listName, items) {
    const list = document.querySelector(`.${listName} .task-list`);

    if (!items.length) {
        renderPlaceholder(list, listName);
        return;
    }

    for (const item of items) {
        list.appendChild(createTaskElement(item, listName));
    }
}

// ----- Task Update Logic ----

// Function to handle checkbox change event
async function handleCheckboxChange(checkbox) {
    const taskLi = checkbox.closest(".task-item");

    // Send update to server
    await fetch("/update_task", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            id: checkbox.dataset.id,
            completed: checkbox.checked
        })
    });

    // Refresh Dashboard according to changes
    refreshDashboard()
}


// Reload dashboard on refresh
document.addEventListener("DOMContentLoaded", (event) => {
    refreshDashboard();
});

// ----- Chat Related Logic -----

const  handleChat = async () => {
    // Read User Message and clear it from input field
    userMessage = chatInput.value.trim();
    chatInput.value = "";
    // Check if it's empty -> return
    if (!userMessage){
        return;
    }
    // Append user message in the chat
    chatbox.appendChild(createChatLi(userMessage, "chat-outgoing"));
    chatbox.scrollTo(0,chatbox.scrollHeight);

    // User gets a message showing "Thinking..."
    let incomingChatLi = createChatLi("Thinking...", "chat-incoming")
    chatbox.appendChild(incomingChatLi);
    chatbox.scrollTo(0,chatbox.scrollHeight);

    // Send message to flask and get response
    try{
        const res = await fetch(url,{
            method: 'POST',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "message": [
                    {
                        role: "user",
                        content: userMessage
                    }
                ]
            }
            )
        });
        // Replace "Thinking..." with the ai response
        const data = await res.json()
        incomingChatLi.querySelector("p").innerHTML = data.response;

        // Update lists Appropriately
        refreshDashboard();
    }
    catch(error){
        incomingChatLi.querySelector("p").textContent =
        "Sorry, something went wrong.";;
    }

}

const createChatLi = (message, className) => {
    const chatLi = document.createElement("li");
    chatLi.classList.add("chat", className);
    let chatContent = 
        className === "chat-outgoing" ? `<p>${message}</p>` : `<p>${message}</p>`;
    chatLi.innerHTML = chatContent;
    return chatLi;
}

sendChatBtn.addEventListener("click", handleChat);
chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleChat();
    }
});