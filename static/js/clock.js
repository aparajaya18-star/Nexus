const clockMode = document.querySelector(".clock-mode");
const timerMode = document.querySelector(".timer-mode");

const clockToggle = document.getElementById("clock-toggle");
const timerToggle = document.getElementById("timer-toggle");

function showClockMode() {
    clockMode.style.display = "flex";
    timerMode.style.display = "none";
}

function showTimerMode() {
    clockMode.style.display = "none";
    timerMode.style.display = "flex";
}

document.addEventListener('DOMContentLoaded', () => {
    showClockMode();
});

clockToggle.addEventListener("click", showTimerMode);
timerToggle.addEventListener("click", showClockMode);

function updateClock() {
    const now = new Date();

    // Format Time (e.g., "03:45:12 PM")
    const timeOptions = { hour: '2-digit', minute: '2-digit', hour12: true };
    const timeString = now.toLocaleTimeString('en-IN', timeOptions);

    // Format Date (e.g., "Monday, July 27, 2026")
    const dateOptions = { weekday: 'long', month: 'long', day: 'numeric' };
    const dateString = now.toLocaleDateString('en-US', dateOptions);

    // Update DOM
    document.getElementById('clock-time').textContent = timeString;
    document.getElementById('clock-date').textContent = dateString;
}

// Run the clock immediately on page load
updateClock();

// Refresh the clock every 1000 milliseconds (1 second)
setInterval(updateClock, 1000);

const timerCircle = document.querySelector(".pomodoro");

const pomodoro = document.getElementById("pomodoro-timer")
const short = document.getElementById("short-timer")
const long = document.getElementById("long-timer")
const timers = document.querySelectorAll(".timer-display")
// Buttons
const session = document.getElementById("pomodoro-session")
const shortBreak = document.getElementById("short-break")
const longBreak = document.getElementById("long-break")
// Controls
const startBtn = document.getElementById("start-button")
const pauseBtn = document.getElementById("pause-button")
const resetBtn = document.getElementById("reset-button")
// Completion Modal
const completionModal = document.getElementById("timer-complete");
const closeComplete = document.getElementById("close-complete");

let totalTime = 0;
let currentTimer = pomodoro;
let myInterval = null;

let remainingTime = Number(currentTimer.dataset.duration) * 60;
let isRunning = false;

// Timer Display
function updateProgress() {
    const progress = (remainingTime / totalTime) * 100;

    timerCircle.style.setProperty(
        "--progress",
        `${progress}%`
    );
}

function updateTimerDisplay() {
    const minutes = Math.floor(remainingTime / 60);
    const seconds = remainingTime % 60;
    const formattedTime = `${minutes}:${seconds.toString().padStart(2, "0")}`;
    const timeText = currentTimer.querySelector(".time");
    timeText.textContent = formattedTime;
    updateProgress();
}

// Timer Selection
function hideAll()  {
    timers.forEach((timer) => (
        timer.style.display = "none"
    ))
}

function selectTimer(timer) {
    clearInterval(myInterval);
    myInterval = null;
    isRunning = false;

    hideAll();
    timer.style.display = "block";
    currentTimer = timer;

    totalTime = Number(currentTimer.dataset.duration) * 60;
    remainingTime = Number(currentTimer.dataset.duration) * 60;

    updateTimerDisplay();
    updateProgress();
}

// Default Timer
selectTimer(pomodoro);

// Timer Buttons

session.addEventListener("click", () => {
    selectTimer(pomodoro)

    session.classList.add("active")
    shortBreak.classList.remove("active")
    longBreak.classList.remove("active")
});

shortBreak.addEventListener("click", () => {
    selectTimer(short)

    session.classList.remove("active")
    shortBreak.classList.add("active")
    longBreak.classList.remove("active")
});

longBreak.addEventListener("click", () => {
    selectTimer(long)

    session.classList.remove("active")
    shortBreak.classList.remove("active")
    longBreak.classList.add("active")
});

// Start the timer on click
function startTimer(timerDisplay) {

    if(isRunning) {
        return;
    }

    if(remainingTime <= 0) {
        remainingTime = Number(timerDisplay.dataset.duration) * 60;
    }

    isRunning = true;

    myInterval = setInterval(() => {
        remainingTime--;

        updateTimerDisplay();

        if (remainingTime <= 0) {

            clearInterval(myInterval);
            myInterval = null;
            isRunning = false;

            remainingTime = 0;
            updateTimerDisplay();

            completionModal.classList.add("open");

            const alarm = new Audio(
                "https://www.freespecialeffects.co.uk/soundfx/scifi/electronic.wav"
            );

            alarm.play().catch(() => {});
        }
    }, 1000);
}

// Pause
function pauseTimer() {

    if (!isRunning) {
        return;
    }

    clearInterval(myInterval);
    myInterval = null;
    isRunning = false;
}

// Reset
function resetTimer() {

    clearInterval(myInterval);
    myInterval = null;
    isRunning = false;

    remainingTime =
        Number(currentTimer.dataset.duration) * 60;

    updateTimerDisplay();
}

// Controls
startBtn.addEventListener("click", () => {
    startTimer(currentTimer);
});
pauseBtn.addEventListener("click", pauseTimer);
resetBtn.addEventListener("click", resetTimer);

closeComplete.addEventListener("click", () => {
    completionModal.classList.remove("open");
    resetTimer();
});