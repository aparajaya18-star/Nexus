// ---------- Constants ----------

const DEFAULT_CATEGORIES = [
    "Food",
    "Transport",
    "Shopping",
    "Entertainment",
    "Bills",
    "Travel",
    "Education",
    "Health",
    "Subscriptions",
    "Technology",
    "Fitness",
    "Gifts",
    "Other"
];

const MAX_DISPLAY_CATEGORIES = 5;

// ---------- State ----------

let budget = 0;
let expenses = [];

// ---------- Elements ----------

const budgetAmount =
    document.getElementById("budget-amount");

const budgetMonth =
    document.getElementById("budget-month");

const spentAmount =
    document.getElementById("spent-amount");

const remainingAmount =
    document.getElementById("remaining-amount");

const remainingMessage =
    document.getElementById("remaining-message");

const budgetPercentage =
    document.getElementById("budget-percentage");

const progressBar =
    document.getElementById("budget-progress-bar");

const topCategory =
    document.getElementById("top-category");

const topCategoryAmount =
    document.getElementById("top-category-amount");

const dailyAverage =
    document.getElementById("daily-average");

const projectedSpending =
    document.getElementById("projected-spending");

const dailyBudgetLeft =
    document.getElementById("daily-budget-left");

const categoryList =
    document.getElementById("category-list");

const expenseList =
    document.getElementById("expense-list");

// ---------- Helpers ----------

function formatCurrency(amount) {
    return `₹${Number(amount).toLocaleString("en-IN", {
        maximumFractionDigits: 2
    })}`;
}

async function loadBudgetData() {

    const response =
        await fetch("/budget/data");

    if (!response.ok) {
        throw new Error("Failed to load budget data.");
    }

    const data =
        await response.json();

    budget = Number(data.budget);
    expenses = data.expenses || [];

    return data;
}

// ---------- Budget Overview ----------

function updateOverview(data) {

    const spent =
        Number(data.spent);

    const remaining =
        Number(data.remaining);

    const percentage =
        Number(data.percentage);

    budgetAmount.textContent =
        formatCurrency(budget);

    budgetMonth.textContent =
        data.month_name;

    spentAmount.textContent =
        `${formatCurrency(spent)} spent`;

    budgetPercentage.textContent =
        `${percentage}%`;

    progressBar.style.width =
        `${Math.min(percentage, 100)}%`;


    if (remaining < 0) {

        remainingAmount.textContent =
            `-${formatCurrency(Math.abs(remaining))}`;

        remainingMessage.textContent =
            "You've gone over your budget.";

    } else {

        remainingAmount.textContent =
            formatCurrency(remaining);

        remainingMessage.textContent =
            "You're within your budget.";

    }


    // Top spending category

    if (data.top_category) {

        topCategory.textContent =
            data.top_category;

        topCategoryAmount.textContent =
            `${formatCurrency(
                data.top_category_amount
            )} this month`;

    } else {

        topCategory.textContent =
            "—";

        topCategoryAmount.textContent =
            "No expenses yet";

    }

}

// ---------- Spending Insights ----------

function updateInsights(data) {

    dailyAverage.textContent =
        formatCurrency(data.daily_average);

    projectedSpending.textContent =
        formatCurrency(data.projected_spending);

    dailyBudgetLeft.textContent =
        formatCurrency(data.daily_budget_left);

}

// ---------- Categories ----------

function renderCategories(data) {

    categoryList.innerHTML = "";

    // Actual categories, already sorted by
    // spending amount by the backend.

    const usedCategories =
        data.categories || [];


    const displayCategories =
        usedCategories
            .map(item => item.category);

    // Fill remaining slots with defaults

    for (const category of DEFAULT_CATEGORIES) {

        if (
            displayCategories.length >=
            MAX_DISPLAY_CATEGORIES
        ) {
            break;
        }

        if (!displayCategories.includes(category)) {
            displayCategories.push(category);
        }

    }

    const categories =
        displayCategories.slice(
            0,
            MAX_DISPLAY_CATEGORIES
        );

    const categoryAmounts = {};

    usedCategories.forEach(item => {

        categoryAmounts[item.category] =
            Number(item.amount);

    });

    const maxAmount =
        Math.max(
            ...categories.map(
                category =>
                    categoryAmounts[category] || 0
            ),
            1
        );

    categories.forEach(category => {

        const amount =
            categoryAmounts[category] || 0;

        const percentage =
            amount > 0
                ? (amount / maxAmount) * 100
                : 0;

        const categoryElement =
            document.createElement("div");

        categoryElement.className =
            "category";

        categoryElement.innerHTML = `
            <div class="category-info">
                <span>${category}</span>
                <span>${formatCurrency(amount)}</span>
            </div>

            <div class="category-bar">
                <div style="width:${percentage}%"></div>
            </div>
        `;

        categoryList.appendChild(
            categoryElement
        );

    });

}

// ---------- Expenses ----------

function renderExpenses() {

    expenseList.innerHTML = "";


    if (expenses.length === 0) {

        expenseList.innerHTML = `
            <p class="empty-state">
                No expenses recorded yet.
            </p>
        `;

        return;
    }

    expenses.forEach(expense => {

        const expenseElement =
            document.createElement("div");


        expenseElement.className =
            "expense-item";


        expenseElement.innerHTML = `
            <div class="expense-info">

                <strong>
                    ${expense.description}
                </strong>

                <span>
                    ${expense.category} · ${expense.date}
                </span>

            </div>

            <div class="expense-actions">

                <strong>
                    ${formatCurrency(expense.amount)}
                </strong>

                <button
                    type="button"
                    class="delete-expense"
                    data-id="${expense.id}"
                >
                    ×
                </button>

            </div>
        `;

        expenseList.appendChild(
            expenseElement
        );

    });

    document
        .querySelectorAll(".delete-expense")
        .forEach(button => {

            button.addEventListener(
                "click",
                async () => {

                    const id =
                        Number(button.dataset.id);


                    try {

                        const response =
                            await fetch(
                                `/budget/expense/${id}`,
                                {
                                    method: "DELETE"
                                }
                            );


                        if (!response.ok) {
                            throw new Error(
                                "Failed to delete expense."
                            );
                        }


                        await render();

                    } catch (error) {

                        console.error(error);

                    }

                }
            );

        });

}

// ---------- Add Expense ----------

document
    .getElementById("expense-form")
    .addEventListener(
        "submit",
        async event => {

            event.preventDefault();

            const description =
                document
                    .getElementById(
                        "expense-description"
                    )
                    .value
                    .trim();

            const amount =
                Number(
                    document
                        .getElementById(
                            "expense-amount"
                        )
                        .value
                );

            const category =
                document
                    .getElementById(
                        "expense-category"
                    )
                    .value;

            const date =
                document
                    .getElementById(
                        "expense-date"
                    )
                    .value;

            if (
                !description ||
                amount <= 0 ||
                !date
            ) {
                return;
            }

            try {

                const response =
                    await fetch(
                        "/budget/expense",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({
                                description,
                                amount,
                                category,
                                date
                            })
                        }
                    );

                if (!response.ok) {
                    throw new Error(
                        "Failed to add expense."
                    );
                }

                event.target.reset();

                setDefaultDate();

                await render();

            } catch (error) {
                console.error(error);
            }

        }
    );

// ---------- Budget Editing ----------

const budgetModal =
    document.getElementById(
        "budget-modal"
    );

document
    .getElementById("edit-budget-btn")
    .addEventListener(
        "click",
        () => {

            document
                .getElementById("new-budget")
                .value = budget;

            budgetModal.classList.add(
                "open"
            );

        }
    );

document
    .getElementById("close-budget-modal")
    .addEventListener(
        "click",
        () => {
            budgetModal.classList.remove(
                "open"
            );
        }
    );

document
    .getElementById("budget-form")
    .addEventListener(
        "submit",
        async event => {
            event.preventDefault();

            const newBudget =
                Number(
                    document
                        .getElementById(
                            "new-budget"
                        )
                        .value
                );

            if (newBudget <= 0) {
                return;
            }

            try {
                const response =
                    await fetch(
                        "/budget",
                        {
                            method: "POST",
                            headers: {
                                "Content-Type":
                                    "application/json"
                            },
                            body: JSON.stringify({
                                amount: newBudget
                            })
                        }
                    );

                if (!response.ok) {
                    throw new Error(
                        "Failed to update budget."
                    );
                }

                budgetModal.classList.remove(
                    "open"
                );

                await render();

            } catch (error) {
                console.error(error);
            }

        }
    );

// ---------- Date ----------

function setDefaultDate() {

    const dateInput =
        document.getElementById(
            "expense-date"
        );

    const today =
        new Date();

    const localDate =
        new Date(
            today.getTime() -
            today.getTimezoneOffset() * 60000
        )
        .toISOString()
        .split("T")[0];

    dateInput.value =
        localDate;
}

// ---------- Render ----------

async function render() {

    try {

        const data =
            await loadBudgetData();

        updateOverview(data);

        updateInsights(data);

        renderCategories(data);

        renderExpenses();

    } catch (error) {
        console.error(
            "Could not load budget:",
            error
        );

    }

}

setDefaultDate();

render();