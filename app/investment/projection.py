import numpy as np
from .explainer import explain_projection

ASSETS = [
    {"name": "Treasury Bills", "risk": "Low", "rate": 0.10, "type": "simple"},
    {"name": "Money Market Fund", "risk": "Low", "rate": 0.11, "type": "compound"},
    {"name": "Unit Trust", "risk": "Medium", "rate": 0.06, "type": "compound"},  # corrected 6%
    {"name": "Balanced Fund", "risk": "Medium", "rate": 0.06, "type": "compound"}, # corrected 6%
    {"name": "Equity Fund", "risk": "High", "rate": 0.18, "type": "compound"},
    {"name": "REITs", "risk": "High", "rate": 0.15, "type": "compound"},
]

RISK_VOLATILITY = {"Low": 0.05, "Medium": 0.10, "High": 0.18}

def monte_carlo_projection(amount, years, mean_return, volatility, simulations=10000):
    results = []
    for _ in range(simulations):
        value = amount
        for _ in range(years):
            yearly_return = np.random.normal(mean_return, volatility)
            value *= (1 + yearly_return)
        results.append(value)
    return {
        "conservative": round(np.percentile(results, 10), 2),
        "expected": round(np.percentile(results, 50), 2),
        "optimistic": round(np.percentile(results, 90), 2)
    }

def recommend_investments(amount, years, risk_level, historical_returns=None):
    risk_level = risk_level.capitalize()
    recommended_assets = [a.copy() for a in ASSETS if a["risk"] == risk_level]

    # Dynamic rules
    if risk_level == "Low" and years < 3:
        recommended_assets = [a for a in recommended_assets if a["name"] == "Treasury Bills"]
    if risk_level == "High" and years >= 5:
        recommended_assets = [a for a in recommended_assets if a["name"] in ["Equity Fund", "REITs"]]

    results = []
    for asset in recommended_assets:
        mean_rate = asset["rate"]
        asset_name_key = asset["name"].rstrip('s')
        if historical_returns and asset_name_key in historical_returns:
            mean_rate = np.mean(historical_returns[asset_name_key])

        volatility = RISK_VOLATILITY[risk_level]
        projection = monte_carlo_projection(amount, years, mean_rate, volatility)

        # Kenya-specific explanation
        detailed_explanation = explain_projection(
            amount=amount,
            years=years,
            risk=risk_level,
            asset_name=asset["name"],
            projection=projection
        )

        results.append({
            "asset_name": asset["name"],
            "interest_type": asset["type"],
            "mean_return": round(mean_rate * 100, 2),
            "projection": projection,
            "detailed_explanation": detailed_explanation
        })

    return results
