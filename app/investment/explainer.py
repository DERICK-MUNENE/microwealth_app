def explain_projection(amount, years, risk, asset_name, projection):
    context = KENYA_CONTEXT.get(asset_name, {})

    return f"""
### Why this investment was selected

Your financial analysis indicates a **{risk.lower()} risk profile**, meaning your
current surplus income is limited and cannot comfortably absorb large losses.

Because of this, **{asset_name}** was selected as it aligns with capital
preservation while still offering reasonable growth.

---

### Kenya-specific context
• Issuer / Market: {context.get("issuer", "Kenyan financial market")}
• Typical options: {", ".join(context.get("examples", []))}
• Why suitable for you: {context.get("why", "Matches your risk profile")}

---

### Projection over {years} years (KSh {amount})

• Conservative outcome: **KSh {projection['conservative']}**
• Expected outcome: **KSh {projection['expected']}**
• Optimistic outcome: **KSh {projection['optimistic']}**

These projections are generated using **Monte Carlo simulation**
based on historical return behavior. They represent possible scenarios,
not guaranteed returns.
"""

KENYA_CONTEXT = {
    "Treasury Bills": {
        "issuer": "Central Bank of Kenya (CBK)",
        "why": "They are government-backed and ideal when cashflow is tight.",
        "examples": ["91-Day T-Bill", "182-Day T-Bill", "364-Day T-Bill"]
    },
    "Money Market Fund": {
        "issuer": "Licensed Kenyan fund managers",
        "why": "They offer liquidity and stable returns with minimal volatility.",
        "examples": ["CIC MMF", "Sanlam MMF", "NCBA MMF"]
    },
    "Unit Trust": {
        "issuer": "Kenyan unit trust providers",
        "why": "They diversify across bonds and equities to reduce risk.",
        "examples": ["CIC Unit Trust", "Britam Unit Trust"]
    },
    "Balanced Fund": {
        "issuer": "Kenyan fund managers",
        "why": "They balance growth and stability by mixing assets.",
        "examples": ["ICEA Lion Balanced Fund"]
    },
    "Equity Fund": {
        "issuer": "NSE-listed equity portfolios",
        "why": "They target long-term capital growth.",
        "examples": ["CIC Equity Fund", "ICEA Lion Equity Fund"]
    },
    "REITs": {
        "issuer": "Capital Markets Authority regulated",
        "why": "They provide exposure to Kenyan real estate without ownership.",
        "examples": ["ILAM Fahari I-REIT", "Acorn D-REIT"]
    }
}
