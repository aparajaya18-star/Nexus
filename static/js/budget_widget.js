// ---------- Elements ----------

const monthlyBudget =
    document.getElementById("monthly-budget");

const moneySpent =
    document.getElementById("money-spent");

const budgetProgressBar =
    document.getElementById("budget-progress-bar");

const budgetPercentage =
    document.getElementById("budget-percentage");

const topCategory =
    document.getElementById("top-category");

const categoryList =
    document.getElementById(
        "dashboard-budget-categories"
    );

// ---------- Helpers ----------

function formatCurrency(amount) {

    return `₹${Number(amount).toLocaleString("en-IN", {
        maximumFractionDigits: 2
    })}`;

}

async function loadBudgetWidget() {

    try {

        const response =
            await fetch("/budget/data");


        if (!response.ok) {
            throw new Error(
                "Failed to load budget data."
            );
        }


        const data =
            await response.json();


        updateBudgetWidget(data);

    } catch (error) {

        console.error(
            "Could not load dashboard budget:",
            error
        );

    }

}


// ---------- Update Widget ----------

function updateBudgetWidget(data) {

    const budget =
        Number(data.budget);

    const spent =
        Number(data.spent);

    const percentage =
        Number(data.percentage);


    monthlyBudget.textContent =
        formatCurrency(budget);

    moneySpent.textContent =
        formatCurrency(spent);

    budgetPercentage.textContent =
        `${percentage}%`;


    budgetProgressBar.style.width =
        `${Math.min(percentage, 100)}%`;


    topCategory.textContent =
        data.top_category || "—";


    renderCategories(
        data.categories || []
    );

}


// ---------- Categories ----------

function renderCategories(categories) {

    categoryList.innerHTML = "";


    const MAX_CATEGORIES = 4;


    const displayCategories =
        categories.slice(
            0,
            MAX_CATEGORIES
        );


    // If there are fewer than four actual
    // categories, fill the remaining slots.

    const defaults = [
        "Food",
        "Transport",
        "Shopping",
        "Other"
    ];


    for (const category of defaults) {

        if (
            displayCategories.length >=
            MAX_CATEGORIES
        ) {
            break;
        }


        const alreadyExists =
            displayCategories.some(
                item =>
                    item.category === category
            );


        if (!alreadyExists) {

            displayCategories.push({
                category,
                amount: 0
            });

        }

    }


    const maxAmount =
        Math.max(
            ...displayCategories.map(
                item => Number(item.amount)
            ),
            1
        );


    displayCategories.forEach(item => {

        const amount =
            Number(item.amount);


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
                <span>${item.category}</span>
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


// ---------- Initial Load ----------

loadBudgetWidget();