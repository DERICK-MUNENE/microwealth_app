import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# Simple risk prediction model
def predict_risk(income, expenses, savings):
    """
    Predict risk level based on financial metrics
    Returns: 'Low', 'Medium', or 'High'
    """
    try:
        # Calculate basic ratios
        expense_ratio = expenses / income if income > 0 else 1
        savings_ratio = savings / income if income > 0 else 0
        
        # Simple rule-based risk assessment
        if expense_ratio > 0.8:
            return "High"
        elif expense_ratio > 0.6:
            return "Medium"
        elif savings_ratio > 0.3:
            return "Low"
        elif savings_ratio > 0.1:
            return "Medium"
        else:
            return "High"
            
    except:
        # Fallback
        return "Medium"
