from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import text as sql_text
from jose import jwt, JWTError
from fastapi.staticfiles import StaticFiles 
from fastapi.responses import HTMLResponse, FileResponse
from decimal import Decimal, ROUND_HALF_UP
import pdfplumber
import tempfile
import time
import json
import os
import re
from typing import List, Optional, Dict
from datetime import datetime  



# Try to import forecaster, but provide fallback
try:
    from app.ml.forecast_model import forecaster
except ImportError:
    # Create a simple fallback forecaster
    class SimpleForecaster:
        def forecast_returns(self, asset_class, years_ahead, historical_returns=None):
            # Default returns if Prophet not installed
            defaults = {
                'Equity': {'expected_annual_return': 0.10, 'confidence_interval': [0.06, 0.14]},
                'Bonds': {'expected_annual_return': 0.05, 'confidence_interval': [0.03, 0.07]},
                'Money Market': {'expected_annual_return': 0.03, 'confidence_interval': [0.02, 0.04]}
            }
            return defaults.get(asset_class, {'expected_annual_return': 0.06, 'confidence_interval': [0.04, 0.08]})
        
        def monte_carlo_simulation(self, initial_amount, monthly_contribution, years, expected_return, volatility):
            import numpy as np
            np.random.seed(42)
            results = []
            for _ in range(1000):
                amount = initial_amount
                for month in range(years * 12):
                    monthly_return = np.random.normal(expected_return/12, volatility/np.sqrt(12))
                    amount = amount * (1 + monthly_return) + monthly_contribution
                results.append(amount)
            results = np.array(results)
            return {
                'median_outcome': np.median(results),
                'probability_positive': (results > initial_amount).mean(),
                'percentile_90': np.percentile(results, 90),
                'percentile_10': np.percentile(results, 10)
            }
    
    forecaster = SimpleForecaster()

from app.pdf.parser import parse_transaction_pdf
from app.database import SessionLocal
from app.auth import hash_password, verify_password, create_access_token
from app.ml.model import predict_risk
from app.investment.explainer import explain_projection
from app.investment.projection import recommend_investments
from app.cashflow.intelligence import analyze_cashflow
from app.cashflow.recovery import cashflow_recovery_plan

# CONFIG 
SECRET_KEY = "MICROWEALTH_SECRET_KEY"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# APP 
app = FastAPI(title="MicroWealth AI Backend")

# ADD THIS: Serve static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# CORS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




# DB 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# AUTH 
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["user_id"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# SCHEMAS 
class RegisterInput(BaseModel):
    full_name: str
    email: EmailStr
    password: str

class LoginInput(BaseModel):
    email: EmailStr
    password: str

class FinanceInput(BaseModel):
    income: float
    expenses: float
    savings: float

class InvestmentProjectionInput(BaseModel):
    amount: float
    years: int

class DashboardRequest(BaseModel):
    time_horizon: int = 5
    amount: Optional[float] = None

class TransactionInput(BaseModel):
    date: Optional[str] = None
    description: str
    amount: float
    balance: Optional[float] = None
    
class InvestmentRequest(BaseModel):
    amount: float
    years: int
    risk_level: str

class CashflowRequest(BaseModel):
    transactions: List[TransactionInput]

# ROUTES 
@app.get("/api")
def home():
    return {"message": "MicroWealth AI Backend Running"}

# REGISTER 
@app.post("/register")
def register(data: RegisterInput, db: Session = Depends(get_db)):

    # 🔍 check email first
    existing = db.execute(
        sql_text("SELECT id FROM users WHERE email = :email"),
        {"email": data.email}
    ).fetchone()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    hashed_pwd = hash_password(data.password)

    db.execute(
        sql_text("""
            INSERT INTO users (full_name, email, password)
            VALUES (:name, :email, :password)
        """),
        {
            "name": data.full_name,
            "email": data.email,
            "password": hashed_pwd
        }
    )
    db.commit()

    return {"message": "User registered successfully"}
# LOGIN 
@app.post("/login")
def login(data: LoginInput, db: Session = Depends(get_db)):
    user = db.execute(
        sql_text("SELECT * FROM users WHERE email = :email"),
        {"email": data.email}
    ).fetchone()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"user_id": user.id, "email": user.email})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email
        }
    }


# MANUAL ANALYSIS
@app.post("/analyze")
def analyze_finances(
    data: FinanceInput,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # ---------------- Calculate disposable income and risk ----------------
    disposable_income = data.income - data.expenses
    risk = predict_risk(data.income, data.expenses, data.savings)

    recommendations = {
        "Low": ["Money Market Fund", "Treasury Bills"],
        "Medium": ["Balanced Funds", "Unit Trusts"],
        "High": ["Equity Funds", "REITs"]
    }

    # ---------------- Insert into database with created_at and source ----------------
    try:
        db.execute(
            sql_text("""
                INSERT INTO financial_data
                (user_id, income, expenses, savings, disposable_income, risk_level, source, created_at)
                VALUES (:uid, :inc, :exp, :sav, :disp, :risk, :source, NOW())
            """),
            {
                "uid": user_id,
                "inc": data.income,
                "exp": data.expenses,
                "sav": data.savings,
                "disp": disposable_income,
                "risk": risk,
                "source": "manual"
            }
        )
        db.commit()
        print(f"[DEBUG] Inserted financial data for user_id={user_id}")  # Debug log

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to insert financial data: {e}")  # Debug log
        raise HTTPException(status_code=500, detail="Failed to save financial data")

    # ---------------- Return JSON response immediately ----------------
    return {
        "disposable_income": round(disposable_income, 2),
        "risk_level": risk,
        "recommendations": recommendations[risk]
    }


# PROJECT INVESTMENT 
@app.post("/project-investment")
def project_user_investment(
    data: InvestmentProjectionInput,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Fetch user's latest risk level
    record = db.execute(
        sql_text("""
            SELECT risk_level
            FROM financial_data
            WHERE user_id = :uid
            ORDER BY created_at DESC
            LIMIT 1
        """),
        {"uid": user_id}
    ).fetchone()

    if not record:
        raise HTTPException(status_code=400, detail="No financial analysis found")

    risk = record.risk_level

    # Fetch historical returns safely
    hist_records = db.execute(
        sql_text("SELECT asset_name, return_value FROM historical_returns")
    ).fetchall()
    historical_returns = {}
    for r in hist_records:
        historical_returns.setdefault(r.asset_name, []).append(float(r.return_value))

    # Generate recommendations with full explanations
    recommendations = recommend_investments(
        amount=data.amount,
        years=data.years,
        risk_level=risk,
        historical_returns=historical_returns or None
    )

    if not recommendations:
        raise HTTPException(status_code=400, detail="No investment recommendations available")

    # Combine all detailed explanations
    all_explanations = "\n\n".join([r['detailed_explanation'] for r in recommendations])

    return {
        "risk_level": risk,
        "investment_recommendations": recommendations,
        "all_explanations": all_explanations
    }

# ENHANCED PROJECTION

@app.post("/project-investment-enhanced")
def project_investment_enhanced(
    data: InvestmentProjectionInput,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1️⃣ Get user's latest risk level
    record = db.execute(
        sql_text("""
            SELECT risk_level
            FROM financial_data
            WHERE user_id = :uid
            ORDER BY created_at DESC
            LIMIT 1
        """),
        {"uid": user_id}
    ).fetchone()

    if not record:
        raise HTTPException(status_code=400, detail="No financial analysis found")

    risk = record.risk_level

    # 2️⃣ Map risk to Kenya-specific asset classes
    risk_to_assets = {
        "Low": ["Treasury Bills", "Money Market Fund"],
        "Medium": ["Balanced Fund", "Unit Trust"],
        "High": ["Equity Fund", "REITs"]
    }
    asset_classes = risk_to_assets.get(risk, ["Balanced Fund"])
    initial_amount = Decimal(str(data.amount))
    years = data.years

    # 3️⃣ Map risk to expected annual return
    risk_returns = {
        "Low": Decimal("0.06"),
        "Medium": Decimal("0.06"),
        "High": Decimal("0.12")
    }
    expected_return = risk_returns.get(risk, Decimal("0.08"))

    # 4️⃣ Build detailed asset info with Kenya-specific context
    assets_info = []
    for asset_name in asset_classes:
        # Simple projections for display
        projection = {
            "conservative": float((initial_amount * (Decimal("1.03") ** years)).quantize(Decimal("0.01"))),
            "expected": float((initial_amount * ((Decimal("1") + expected_return) ** years)).quantize(Decimal("0.01"))),
            "optimistic": float((initial_amount * (Decimal("1.09") ** years)).quantize(Decimal("0.01")))
        }

        detailed_explanation = explain_projection(
            amount=float(initial_amount),
            years=years,
            risk=risk,
            asset_name=asset_name,
            projection=projection
        )

        assets_info.append({
            "asset_name": asset_name,
            "asset_type": "Kenya-specific",
            "expected_return": float(expected_return),
            "detailed_explanation": detailed_explanation
        })

    # 5️⃣ Optionally: Monte Carlo simulation
    monte_carlo = forecaster.monte_carlo_simulation(
        initial_amount=float(initial_amount),
        monthly_contribution=0,
        years=years,
        expected_return=float(expected_return),
        volatility=0.15
    )

    # 6️⃣ Prepare final projection
    projected_amount = initial_amount * ((Decimal("1") + expected_return) ** years)

    return {
        "risk_level": risk,
        "recommended_assets": assets_info,
        "projection": {
            "initial_amount": float(initial_amount),
            "years": years,
            "expected_amount": float(projected_amount.quantize(Decimal("0.01"))),
            "expected_annual_return": float(expected_return)
        },
        "monte_carlo_simulation": {
            "median_outcome": round(monte_carlo['median_outcome'], 2),
            "probability_positive": round(monte_carlo['probability_positive'], 4),
            "best_10_percent": round(monte_carlo['percentile_90'], 2),
            "worst_10_percent": round(monte_carlo['percentile_10'], 2)
        }
    }
# DASHBOARD DATA ENDPOINT
@app.get("/dashboard/data")
def get_dashboard_data(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get data for dashboard display safely using Decimal."""
    
    # ---------------- Get user's latest financial data ----------------
    financial_data = db.execute(
        sql_text("""
            SELECT income, expenses, savings, risk_level, disposable_income, created_at
            FROM financial_data
            WHERE user_id = :uid
            ORDER BY created_at DESC
            LIMIT 1
        """),
        {"uid": user_id}
    ).fetchone()
    
    if not financial_data:
        return {"error": "No financial data found"}
    
    # ---------------- Get user info ----------------
    user = db.execute(
        sql_text("SELECT full_name FROM users WHERE id = :uid"),
        {"uid": user_id}
    ).fetchone()
    
    # ---------------- Convert all numeric DB values to Decimal ----------------
    income = Decimal(financial_data.income)
    expenses = Decimal(financial_data.expenses)
    savings = Decimal(financial_data.savings)
    disposable_income = Decimal(financial_data.disposable_income)
    
    # ---------------- Metrics ----------------
    savings_rate = (savings / income * Decimal('100')) if income > 0 else Decimal('0')
    expense_ratio = (expenses / income * Decimal('100')) if income > 0 else Decimal('0')
    
    # ---------------- Simple projection ----------------
    projection_amount = savings * Decimal('0.3')  # 30% of savings
    risk = financial_data.risk_level
    
    # Expected returns based on risk
    risk_returns = {
        "Low": Decimal('0.06'),
        "Medium": Decimal('0.09'),
        "High": Decimal('0.12')
    }
    
    expected_return = risk_returns.get(risk, Decimal('0.08'))
    projected_5yr = projection_amount * ((Decimal('1') + expected_return) ** Decimal('5'))
    
    # ---------------- Prepare JSON response ----------------
    response = {
        "user": {
            "name": user.full_name if user else "User",
            "risk_level": risk,
            "last_analysis": financial_data.created_at.isoformat() if financial_data.created_at else None
        },
        "metrics": {
            "monthly_income": float(income.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            "monthly_expenses": float(expenses.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            "monthly_savings": float(savings.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            "disposable_income": float(disposable_income.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            "savings_rate": float(savings_rate.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)),
            "expense_ratio": float(expense_ratio.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)),
            "investment_capacity": float((disposable_income * Decimal('0.3')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        },
        "projection": {
            "recommended_investment": float(projection_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            "expected_return": float(expected_return),
            "projected_5yr": float(projected_5yr.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            "confidence": "medium" if risk == "Medium" else "low" if risk == "Low" else "high"
        },
        "recommendations": {
            "Low": ["Money Market Funds", "Government Bonds", "High-Yield Savings"],
            "Medium": ["Balanced Mutual Funds", "Index Funds", "REITs"],
            "High": ["Growth Stocks", "Technology ETFs", "International Funds"]
        }.get(risk, [])
    }
    
    return response

@app.post("/analyze-pdf")
def analyze_pdf(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # ---------------- VALIDATE FILE ----------------
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    # ---------------- SAVE PDF ----------------
    uploads_dir = "uploads"
    os.makedirs(uploads_dir, exist_ok=True)
    safe_filename = f"user_{user_id}_{int(time.time())}_{file.filename}"
    pdf_save_path = os.path.join(uploads_dir, safe_filename)

    with open(pdf_save_path, "wb") as f:
        f.write(file.file.read())

    # ---------------- PARSE PDF ----------------
    try:
        result = parse_transaction_pdf(pdf_save_path)
    except Exception as e:
        os.remove(pdf_save_path)
        raise HTTPException(status_code=400, detail=str(e))

    income = result["income"]
    expenses = result["expenses"]
    net_cashflow = result["net_cashflow"]
    transactions = result.get("transactions", [])

       # ---------------- STORE PDF METADATA ----------------
    file_size = os.path.getsize(pdf_save_path)
    pages_count = result.get("pages_count", 1)
    
    try:
        analysis_json = json.dumps(result)
    
        result_insert = db.execute(
            sql_text("""
                INSERT INTO pdf_uploads
                (user_id, filename, file_path, file_size, pages_count, analysis_result, upload_status)
                VALUES (:uid, :name, :path, :size, :pages, :result, :status)
            """),
            {
                "uid": user_id,
                "name": safe_filename,
                "path": pdf_save_path,
                "size": file_size,
                "pages": pages_count,
                "result": analysis_json,
                "status": "completed"
            }
        )
    
        pdf_id = result_insert.lastrowid
    
        db.commit()
    
    except Exception as e:   
        os.remove(pdf_save_path)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save PDF metadata: {str(e)}"
        )

    # ---------------- STORE TRANSACTIONS ----------------
    try:
        # Get the last inserted PDF id
        pdf_id = db.execute(sql_text("SELECT LAST_INSERT_ID()")).scalar()
        for tx in transactions:
            
            db.execute(
                sql_text("""
                    INSERT INTO transactions (user_id, pdf_id, description, amount)
                    VALUES (:uid, :pdf, :desc, :amt)
                """),
                {
                    "uid": user_id,
                    "pdf": pdf_id,
                    "desc": tx["description"],
                    "amt": tx["amount"]
                }
            )
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save transactions: {str(e)}")

    # ---------------- CASHFLOW ANALYSIS ----------------
    if net_cashflow <= 0:
        intelligence = analyze_cashflow(transactions)
        recovery = cashflow_recovery_plan(transactions)

        # Clear previous expense breakdown
        db.execute(sql_text("DELETE FROM expense_breakdown WHERE user_id = :uid"), {"uid": user_id})

        # Save new breakdown
        for leak in recovery.get("top_expense_leaks", []):
            db.execute(
                sql_text("""
                    INSERT INTO expense_breakdown (user_id, category, monthly_amount)
                    VALUES (:uid, :cat, :amt)
                """),
                {
                    "uid": user_id,
                    "cat": leak["category"],
                    "amt": leak["monthly_amount"]
                }
            )

        # Format guidance
        guidance_list = [
            "Pause investing immediately",
            "Reduce high-impact expenses",
            "Stabilize cashflow before building portfolio",
            "Suggested daily cuts by category:"
        ]
        for leak in recovery.get("top_expense_leaks", []):
            daily_cut = round(leak["monthly_amount"] / 30, 2)
            guidance_list.append(f"- {leak['category'].capitalize()}: KSh {daily_cut}/day")

        # Save financial record
        db.execute(
            sql_text("""
                INSERT INTO financial_data
                (user_id, income, expenses, savings, disposable_income, risk_level, source, created_at)
                VALUES (:uid, :inc, :exp, :sav, :disp, :risk, :source, NOW())
            """),
            {
                "uid": user_id,
                "inc": income,
                "exp": expenses,
                "sav": net_cashflow,
                "disp": net_cashflow,
                "risk": "Negative Cashflow",
                "source": "pdf"
            }
        )
        db.commit()

        return {
            "status": "financially_unstable",
            "income": income,
            "expenses": expenses,
            "net_cashflow": net_cashflow,
            "investment_allowed": False,
            "recovery_plan": recovery,
            "guidance": guidance_list,
            **intelligence
        }

    # ---------------- POSITIVE CASHFLOW ----------------
    if net_cashflow < 5000:
        risk = "Low"
        recommendations = ["Money Market Fund", "Treasury Bills"]
    elif net_cashflow < 15000:
        risk = "Medium"
        recommendations = ["Unit Trusts", "Balanced Funds"]
    else:
        risk = "High"
        recommendations = ["Equity Funds"]

    # Clear old breakdown if previously unstable
    db.execute(sql_text("DELETE FROM expense_breakdown WHERE user_id = :uid"), {"uid": user_id})

    # Save financial record
    db.execute(
        sql_text("""
            INSERT INTO financial_data
            (user_id, income, expenses, savings, disposable_income, risk_level, source, created_at)
            VALUES (:uid, :inc, :exp, :sav, :disp, :risk, :source, NOW())
        """),
        {
            "uid": user_id,
            "inc": income,
            "exp": expenses,
            "sav": net_cashflow,
            "disp": net_cashflow,
            "risk": risk,
            "source": "pdf"
        }
    )
    db.commit()

    return {
        "status": "financially_stable",
        "income": income,
        "expenses": expenses,
        "net_cashflow": net_cashflow,
        "risk_level": risk,
        "investment_allowed": True,
        "recommendations": recommendations
    }

def categorize_transaction(description: str) -> str:
    """
    Maps a transaction description to an expense category.
    """
    desc = description.lower()

    if "pay bill" in desc:
        return "Utilities & Bills"
    elif "send money" in desc:
        return "Transfers"
    elif "fsi deposit" in desc or "fsi withdraw" in desc:
        return "Bank Transactions"
    elif "customer bundle purchase" in desc or "airtime" in desc:
        return "Daily Expenses"
    elif "b2c payment" in desc or "customer merchant payment" in desc:
        return "Business / Income"
    else:
        return "Other"

@app.post("/cashflow-from-latest-pdf")
def cashflow_from_latest_pdf(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # ---------------- FETCH LATEST PDF ----------------
    pdf_row = db.execute(
        sql_text("""
            SELECT id FROM pdf_uploads
            WHERE user_id = :uid
            ORDER BY uploaded_at DESC
            LIMIT 1
        """),
        {"uid": user_id}
    ).fetchone()

    if not pdf_row:
        raise HTTPException(status_code=404, detail="No uploaded PDF found for this user")

    pdf_id = pdf_row[0]

    # ---------------- FETCH TRANSACTIONS ----------------
    tx_rows = db.execute(
        sql_text("""
            SELECT description, amount FROM transactions
            WHERE user_id = :uid AND pdf_id = :pdf
        """),
        {"uid": user_id, "pdf": pdf_id}
    ).fetchall()

    if not tx_rows:
        raise HTTPException(status_code=404, detail="No transactions found for the latest PDF")

    transactions = [{"description": row[0], "amount": float(row[1])} for row in tx_rows]

    # ---------------- CALCULATE CASHFLOW ----------------
    income = sum(tx["amount"] for tx in transactions if tx["amount"] > 0 and not tx["description"].upper().startswith("TOTAL"))
    expenses_total = sum(-tx["amount"] for tx in transactions if tx["amount"] < 0 and not tx["description"].upper().startswith("TOTAL"))
    net_cashflow = income - expenses_total

    # ---------------- STORE EXPENSES ----------------
    # Categorize transactions for expense_breakdown
    expense_categories = {}
    for tx in transactions:
        if tx["amount"] < 0 and not tx["description"].upper().startswith("TOTAL"):
            # Simple category assignment; you can expand this
            category = tx["description"] or "Other"
            expense_categories[category] = expense_categories.get(category, 0) + (-tx["amount"])

    # Insert into expense_breakdown if not exists
    for category, amount in expense_categories.items():
        exists = db.execute(
            sql_text("""
                SELECT id FROM expense_breakdown
                WHERE user_id = :uid AND category = :cat
            """),
            {"uid": user_id, "cat": category}
        ).fetchone()
        if not exists:
            db.execute(
                sql_text("""
                    INSERT INTO expense_breakdown (user_id, category, monthly_amount, created_at)
                    VALUES (:uid, :cat, :amt, :now)
                """),
                {"uid": user_id, "cat": category, "amt": amount, "now": datetime.now()}
            )
    db.commit()

    # ---------------- PREPARE EXPENSE BREAKDOWN ----------------
    expense_breakdown = [{"category": k, "amount": v} for k, v in expense_categories.items()]

    # ---------------- GENERATE EXPENSE-CUTTING PLAN ----------------
    expense_cutting_plan = []
    for exp in expense_breakdown:
        if exp["amount"] > 20000:
            advice = "High expense. Review subscriptions and consider cheaper alternatives."
        elif exp["amount"] > 10000:
            advice = "Moderate expense. Look for ways to reduce unnecessary spending."
        else:
            advice = "Low expense. Keep monitoring to avoid increases."
        expense_cutting_plan.append({"category": exp["category"], "advice": advice})

    # ---------------- ANALYZE CASHFLOW ----------------
    if net_cashflow <= 0:
        intelligence = analyze_cashflow(transactions)  # your existing function
        recovery = cashflow_recovery_plan(transactions)  # your existing function
        return {
            "status": "financially_unstable",
            "income": round(income, 2),
            "expenses": round(expenses_total, 2),
            "net_cashflow": round(net_cashflow, 2),
            "investment_allowed": False,
            "recovery_plan": recovery,
            "guidance": intelligence.get("guidance"),
            "expense_breakdown": expense_breakdown,
            "expense_cutting_plan": expense_cutting_plan
        }

    # ---------------- POSITIVE CASHFLOW ----------------
    if net_cashflow < 5000:
        risk = "Low"
        recommendations = ["Money Market Fund", "Treasury Bills"]
    elif net_cashflow < 15000:
        risk = "Medium"
        recommendations = ["Unit Trusts", "Balanced Funds"]
    else:
        risk = "High"
        recommendations = ["Equity Funds"]

    return {
        "status": "financially_stable",
        "income": round(income, 2),
        "expenses": round(expenses_total, 2),
        "net_cashflow": round(net_cashflow, 2),
        "risk_level": risk,
        "investment_allowed": True,
        "recommendations": recommendations,
        "expense_breakdown": expense_breakdown,
        "expense_cutting_plan": expense_cutting_plan
    }


@app.get("/history")
def get_financial_history(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print(f"[DEBUG] Fetching history for user_id={user_id}")  # debug print
    records = db.execute(
        sql_text("""
            SELECT id, income, expenses, savings, disposable_income, risk_level, created_at
            FROM financial_data
            WHERE user_id = :uid
            ORDER BY created_at DESC
        """),
        {"uid": user_id}
    ).fetchall()

    print(f"[DEBUG] Fetched {len(records)} records")  # debug print

    return [
        {
           "id": r.id,
            "income": float(r.income),
            "expenses": float(r.expenses),
            "savings": float(r.savings),
            "disposable_income": float(r.disposable_income),
            "risk_level": r.risk_level,
            "date": r.created_at.isoformat() if r.created_at else None
        }
        for r in records
    ]

# USER PROFILE
@app.get("/user/profile")
def get_user_profile(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user profile information"""
    user = db.execute(
        sql_text("SELECT id, full_name, email, created_at FROM users WHERE id = :uid"),
        {"uid": user_id}
    ).fetchone()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Count analyses
    analysis_count = db.execute(
        sql_text("SELECT COUNT(*) as count FROM financial_data WHERE user_id = :uid"),
        {"uid": user_id}
    ).fetchone()
    
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "joined_date": user.created_at.isoformat() if user.created_at else None,
        "analysis_count": analysis_count[0] if analysis_count else 0
    }

# ------------------ LIVE CBK RATES ------------------
@app.get("/cbk-rates")
def get_cbk_rates():
    """
    Returns sample Central Bank of Kenya rates in JSON.
    JS expects each item to have `tenor` and `rate`.
    """
    cbk_rates = [
        {"tenor": "Central Bank Rate (CBR)", "rate": 9.0},
        {"tenor": "Inflation Rate", "rate": 4.4},
        {"tenor": "91-Day T-Bill", "rate": 7.73},
        {"tenor": "182-Day T-Bill", "rate": 8.59},
        {"tenor": "364-Day T-Bill", "rate": 9.15}
    ]
    return cbk_rates


# Serve main HTML pages
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    try:
        return FileResponse("frontend/index.html")
    except:
        return {"message": "MicroWealth AI Backend Running"}

@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    try:
        return FileResponse("frontend/dashboard.html")
    except:
        return {"error": "Dashboard file not found"}

# ------------------ STATIC ASSETS ------------------


# Optional catch-all for older scripts that request static files directly
# Only allow serving from static folder to avoid API conflicts
@app.get("/static/{filename:path}")
async def serve_static(filename: str):
    try:
        return FileResponse(f"static/{filename}")
    except:
        raise HTTPException(status_code=404, detail="File not found")
