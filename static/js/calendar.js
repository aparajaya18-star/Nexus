const calendarDays = document.getElementById('calendar-days');
const prevButton = document.getElementById("prev-month");
const nextButton = document.getElementById("next-month");
let currentDate = new Date();
let displayedMonth = currentDate.getMonth();
let displayedYear = currentDate.getFullYear();
const monthNames = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ];

async function renderCalendar(month=displayedMonth, year=displayedYear) {

    const firstDay = (new Date(year, month, 1).getDay() + 6) % 7;
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    const dict_events = await fetch('/calendar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ month: month + 1, year: year })
    }).then(response => response.json());

    // Update month and year display
    document.getElementById("calendar-month").textContent = monthNames[month];
    document.getElementById("calendar-year").textContent = year;

    // Clear previous days 
    calendarDays.innerHTML = '';

    // Add empty cells for days of the week before the first day of the month
    for (let i = 0; i < firstDay; i++) {
        const emptyCell = document.createElement('div');
        emptyCell.classList.add('calendar-date', 'empty');
        calendarDays.appendChild(emptyCell);
    }

    // Add dates for the current month
    for (let day = 1; day <= daysInMonth; day++) {
        const dayCell = document.createElement('div');
        const events = dict_events[day];

        dayCell.classList.add('calendar-date');
        const dayNumber = document.createElement('div');
        // Add a class for styling the day number
        dayNumber.classList.add('day-number');
        dayNumber.textContent = day;
        dayCell.appendChild(dayNumber);

        if (events && events.length > 0) {
            dayCell.classList.add("has-event");

            // Create a preview of events for the day
            const eventPreview = document.createElement("div");
            eventPreview.classList.add("event-preview");;
            dayCell.appendChild(eventPreview);
            const eventList = document.createElement("ul");
            events.forEach(event => {
                const eventItem = document.createElement("li");
                eventItem.textContent = "●";
                // Later add a +2 more events indicator if there are more than x events
                eventList.appendChild(eventItem);
            });

            eventPreview.appendChild(eventList);

            // Add popup on hover to show events
            const popup = document.createElement('div');
            popup.classList.add('event-popup');
            popup.innerHTML = events.map(event => `<div class="event-item"><strong>${event["time"]}</strong> - ${event["title"]} <br> ${event["details"] || ''}</div>`).join('');
            dayCell.appendChild(popup);
        }

        if (
            day === currentDate.getDate() &&
            month === currentDate.getMonth() &&
            year === currentDate.getFullYear()
        ) {
            dayCell.classList.add("today");
        }

        calendarDays.appendChild(dayCell);
        
    }

}

prevButton.addEventListener("click", () => {
    displayedMonth--;

    if (displayedMonth < 0) {
        displayedMonth = 11; // December
        displayedYear--;
    }

    renderCalendar(displayedMonth, displayedYear);
});

nextButton.addEventListener("click", () => {
    displayedMonth++;

    if (displayedMonth > 11) {
        displayedMonth = 0; // January
        displayedYear++;
    }

    renderCalendar(displayedMonth, displayedYear);
});

document.addEventListener("DOMContentLoaded", (event) => {
    renderCalendar();
});