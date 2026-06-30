const chatInput = 
    document.querySelector(".chat-input textarea");
const sendChatBtn =
    document.querySelector(".chat-input button");
const chatbox = document.querySelector('.chatbox')
const url = "/chat";
let userMessage;

// Function to handle checkbox change event
async function handleCheckboxChange(checkbox) {
    taskLi = checkbox.closest(".task-item");
    taskLi.classList.toggle("completed", checkbox.checked);

    // Move completed items to bottom
    const list = taskLi.closest(".task-list");
    if (checkbox.checked) {
        list.appendChild(taskLi);      // move to bottom
    } else {
        list.prepend(taskLi);          // move back to top
    }

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
    }

// Function to maintain checked state of checkboxes and attach event listeners upon page load
function attachCheckboxListener()
{
    const checkboxes = document.querySelectorAll(".task-check");
    checkboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", () => {
            handleCheckboxChange(checkbox);
        });
    });
}

// Attach event listener to checkboxes on page load
document.addEventListener("DOMContentLoaded", (event) => {
    attachCheckboxListener();
});

const createChatLi = (message, className) => {
    const chatLi = document.createElement("li");
    chatLi.classList.add("chat", className);
    let chatContent = 
        className === "chat-outgoing" ? `<p>${message}</p>` : `<p>${message}</p>`;
    chatLi.innerHTML = chatContent;
    return chatLi;
}

const addItemToList = (item) => {

    const list = document.querySelector(`.${item.intent.toLowerCase()} .task-list`);

    // Remove placeholder if it exists
    const placeholder = list.querySelector(".placeholder");
    if (placeholder) placeholder.remove();

    const taskLi = document.createElement("li");
    taskLi.classList.add("task-item");

    // Add new item to list based on intent
    switch(item.intent){

        case "Todo":
            taskLi.innerHTML = `
                <label class="task-entry">
                    <input type="checkbox" class="task-check" data-id="${item.id}">
                    <span>${item.title}</span>
                </label>
            `;
            break;

        case "Deadline":
            taskLi.innerHTML = `
                <label class="task-entry">
                    <input type="checkbox" class="task-check" data-id="${item.id}">
                    <div>
                        <strong>${item.title}</strong><br>
                        📅 ${item.date ?? "-"}<br>
                        🕒 ${item.time ?? "-"}
                    </div>
                </label>
            `;
            break;

        case "Goal":
            taskLi.innerHTML = `
                <label class="task-entry">
                    <input type="checkbox" class="task-check" data-id="${item.id}">
                    <div>
                        <strong>🎯 ${item.title}</strong>
                        ${item.details ? `<br>${item.details}` : ""}
                    </div>
                </label>
            `;
            break;
    }

    // Checkbox event
    const checkbox = taskLi.querySelector(".task-check");

    checkbox.addEventListener("change", () => {
        handleCheckboxChange(checkbox)
    });

    list.appendChild(taskLi);
}

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
        for (const task of data.classification.tasks) {
            if (
                task &&
                task.intent &&
                task.intent !== "Chat"
                ) {
                    addItemToList(task);
                }
        }   
    }
    catch(error){
        incomingChatLi.querySelector("p").textContent =
        "Sorry, something went wrong.";;
    }

}

sendChatBtn.addEventListener("click", handleChat);
chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleChat();
    }
});