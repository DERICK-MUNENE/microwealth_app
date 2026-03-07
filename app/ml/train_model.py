import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import numpy as np

# Generate synthetic data
np.random.seed(42)

data = pd.DataFrame({
    "income": np.random.randint(20000, 200000, 500),
    "expenses": np.random.randint(15000, 150000, 500),
    "savings": np.random.randint(0, 50000, 500)
})

def label_risk(row):
    disposable = row["income"] - row["expenses"]
    if disposable < 5000:
        return "Low"
    elif disposable < 15000:
        return "Medium"
    else:
        return "High"

data["risk"] = data.apply(label_risk, axis=1)

# Encode labels
encoder = LabelEncoder()
data["risk_encoded"] = encoder.fit_transform(data["risk"])

X = data[["income", "expenses", "savings"]]
y = data["risk_encoded"]

model = RandomForestClassifier(n_estimators=100)
model.fit(X, y)

# Save model and encoder
joblib.dump(model, "app/ml/risk_model.pkl")
joblib.dump(encoder, "app/ml/encoder.pkl")

print("Model trained and saved successfully")
