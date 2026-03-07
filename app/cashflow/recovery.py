import re
from collections import defaultdict

# Updated categories matching common PDF transactions
CATEGORIES = {
    "money_transfer": ["send money", "b2c payment", "odrepayment", "transfer"],
    "bills": ["pay bill", "fsi deposit", "electricity", "water", "internet"],
    "cash": ["cash in", "atm withdrawal"],
    "merchant": ["customer merchant payment", "customer bundle purchase", "shopping", "supermarket"],
    "airtime": ["airtime purchase", "top up"]
}

def categorize_transaction(description: str):
    """
    Categorize a transaction based on keywords.
    Falls back to 'others' if no match.
    """
    desc = description.lower()
    for category, keywords in CATEGORIES.items():
        for word in keywords:
            if word in desc:
                return category
    return "others"

def cashflow_recovery_plan(transactions: list):
    """
    Generates a recovery plan based on negative cashflow transactions.
    Always returns top expense leaks including 'Others' if needed.
    """
    category_totals = defaultdict(float)
    total_income = 0
    total_expenses = 0

    for tx in transactions:
        amount = tx.get("amount", 0)
        description = tx.get("description", "Transaction") or "Transaction"

        if amount > 0:
            total_income += amount
        elif amount < 0:
            expense = abs(amount)
            total_expenses += expense
            category = categorize_transaction(description)
            category_totals[category] += expense

    net_cashflow = total_income - total_expenses

    # If no deficit → no recovery needed
    if net_cashflow >= 0:
        return {
            "monthly_deficit": 0,
            "recommended_daily_cut": 0,
            "recommended_weekly_cut": 0,
            "top_expense_leaks": []
        }

    monthly_deficit = abs(net_cashflow)

    # Sort biggest expense leaks
    sorted_leaks = sorted(
        category_totals.items(),
        key=lambda x: x[1],
        reverse=True
    )

    top_leaks = sorted_leaks[:3]

    # Ensure at least one category is returned
    if not top_leaks and category_totals:
        # Take the first item in category_totals
        top_leaks = list(category_totals.items())[:1]

    # Required minimum daily cut
    required_daily_cut = round(monthly_deficit / 30, 2)

    return {
        "monthly_deficit": round(monthly_deficit, 2),
        "recommended_daily_cut": required_daily_cut,
        "recommended_weekly_cut": round(required_daily_cut * 7, 2),
        "top_expense_leaks": [
            {
                "category": cat if cat != "others" else "Miscellaneous",
                "monthly_amount": round(amt, 2)
            }
            for cat, amt in top_leaks
        ]
    }
