
from collections import defaultdict

CATEGORIES = {
    "essentials": ["rent", "food", "transport", "fuel", "electricity"],
    "discretionary": ["airtime", "bundle", "entertainment", "subscription"],
    "leaks": ["charge", "fee", "levy", "commission"]
}

def categorize(description: str):
    desc = description.lower()
    for cat, keywords in CATEGORIES.items():
        if any(k in desc for k in keywords):
            return cat
    return "uncategorized"


def analyze_cashflow(transactions: list):
    income = 0
    expenses = 0
    category_totals = defaultdict(float)
    leak_counter = defaultdict(int)

    for tx in transactions:
        amount = tx["amount"]
        desc = tx.get("description", "")

        if amount > 0:
            income += amount
        else:
            expenses += abs(amount)
            cat = categorize(desc)
            category_totals[cat] += abs(amount)

            if cat == "leaks":
                leak_counter[desc] += 1

    net = income - expenses

    expense_total = sum(category_totals.values()) or 1
    breakdown = {
        k: round((v / expense_total) * 100, 2)
        for k, v in category_totals.items()
    }

    leaks = [
        {
            "description": k,
            "occurrences": v
        }
        for k, v in leak_counter.items() if v >= 3
    ]

    daily_fix = abs(net) / 30 if net < 0 else 0

    return {
        "summary": {
            "income": round(income, 2),
            "expenses": round(expenses, 2),
            "net_cashflow": round(net, 2)
        },
        "expense_breakdown": breakdown,
        "leaks_detected": leaks,
        "daily_fix": round(daily_fix, 2),
        "investment_allowed": net > 0
    }