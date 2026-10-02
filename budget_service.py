from datetime import datetime
from database import sqlite_connection


DEFAULT_BUDGET = 10000


def get_monthly_budget():
    now = datetime.now()

    result = sqlite_connection.execute(
        """
        SELECT amount
        FROM BUDGETS
        WHERE month=? AND year=?
        """,
        (now.month, now.year)
    ).fetchone()

    if result:
        return result[0]

    # Create default budget for the current month
    sqlite_connection.execute(
        """
        INSERT INTO BUDGETS (month, year, amount)
        VALUES (?, ?, ?)
        """,
        (now.month, now.year, DEFAULT_BUDGET)
    )

    sqlite_connection.commit()

    return DEFAULT_BUDGET


def set_monthly_budget(amount):
    now = datetime.now()

    sqlite_connection.execute(
        """
        INSERT INTO BUDGETS (month, year, amount)
        VALUES (?, ?, ?)
        ON CONFLICT(month, year)
        DO UPDATE SET amount=excluded.amount
        """,
        (now.month, now.year, amount)
    )

    sqlite_connection.commit()


def get_expenses():
    rows = sqlite_connection.execute(
        """
        SELECT id, description, amount, category, expense_date
        FROM EXPENSES
        ORDER BY expense_date DESC, id DESC
        """
    ).fetchall()

    return [
        {
            "id": row[0],
            "description": row[1],
            "amount": row[2],
            "category": row[3],
            "date": row[4]
        }
        for row in rows
    ]


def add_expense(description, amount, category, expense_date):
    cursor = sqlite_connection.execute(
        """
        INSERT INTO EXPENSES
        (description, amount, category, expense_date)
        VALUES (?, ?, ?, ?)
        """,
        (description, amount, category, expense_date)
    )

    sqlite_connection.commit()

    return cursor.lastrowid


def delete_expense(expense_id):
    sqlite_connection.execute(
        "DELETE FROM EXPENSES WHERE id=?",
        (expense_id,)
    )

    sqlite_connection.commit()


def get_budget_summary():
    now = datetime.now()

    budget = get_monthly_budget()

    rows = sqlite_connection.execute(
        """
        SELECT id, description, amount, category, expense_date
        FROM EXPENSES
        WHERE strftime('%Y', expense_date)=?
        AND strftime('%m', expense_date)=?
        ORDER BY expense_date DESC, id DESC
        """,
        (
            str(now.year),
            f"{now.month:02d}"
        )
    ).fetchall()

    expenses = [
        {
            "id": row[0],
            "description": row[1],
            "amount": row[2],
            "category": row[3],
            "date": row[4]
        }
        for row in rows
    ]

    spent = sum(expense["amount"] for expense in expenses)
    remaining = budget - spent

    percentage = (
        round((spent / budget) * 100)
        if budget > 0
        else 0
    )

    # Category totals
    category_totals = {}

    for expense in expenses:
        category = expense["category"]

        category_totals[category] = (
            category_totals.get(category, 0)
            + expense["amount"]
        )

    categories = [
        {
            "category": category,
            "amount": amount
        }
        for category, amount
        in sorted(
            category_totals.items(),
            key=lambda item: item[1],
            reverse=True
        )
    ]

    if categories:
        top_category = categories[0]["category"]
        top_category_amount = categories[0]["amount"]
    else:
        top_category = None
        top_category_amount = 0

    current_day = now.day

    days_in_month = (
        datetime(
            now.year + (now.month == 12),
            1 if now.month == 12 else now.month + 1,
            1
        ) - datetime(
            now.year,
            now.month,
            1
        )
    ).days

    daily_average = (
        spent / current_day
        if current_day > 0
        else 0
    )

    projected_spending = daily_average * days_in_month

    remaining_days = max(
        days_in_month - current_day,
        1
    )

    daily_budget_left = (
        remaining / remaining_days
        if remaining > 0
        else 0
    )

    return {
        "budget": budget,
        "spent": spent,
        "remaining": remaining,
        "percentage": percentage,
        "month": now.month,
        "year": now.year,
        "month_name": now.strftime("%B %Y"),
        "top_category": top_category,
        "top_category_amount": top_category_amount,
        "daily_average": daily_average,
        "projected_spending": projected_spending,
        "daily_budget_left": daily_budget_left,
        "categories": categories,
        "expenses": expenses
    }