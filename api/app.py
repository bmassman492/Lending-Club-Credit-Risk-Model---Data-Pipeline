from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
import os

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "ml")
model = joblib.load(os.path.join(MODEL_DIR, "model.pkl"))
config = joblib.load(os.path.join(MODEL_DIR, "model_config.pkl"))
THRESHOLD = config["threshold"]
FEATURES = config["features"]

app = FastAPI()

class LoanApplication(BaseModel):
    LOAN_AMOUNT: float
    LOAN_TERM_MONTHS: int
    LOAN_INTEREST_RATE: float
    LOAN_PURPOSE_IS_DEBT_CONSOLIDATION: int
    LOAN_EMP_LENGTH: int
    LOAN_OWNS_HOME: int
    LOAN_ANNUAL_INCOME: float
    LOAN_APPLYING_AS_INDIVIDUAL: int
    LOAN_DTI: float
    LOAN_FICO_RANGE_LOW: int
    LOAN_EARLIEST_CR_LINE: int
    LOAN_OPEN_ACC: int
    LOAN_DELINQ_2YRS: int
    LOAN_INQ_LAST_6MTHS: int
    LOAN_TOT_HI_CRED_LIM: float
    LOAN_TOTAL_BC_LIMIT: float
    LOAN_MORT_ACC: int
    LOAN_BC_UTIL: float
    GDP: float
    FEDERAL_FUNDS_RATE: float
    FIXED_MORTGAGE_RATE: float
    PERSONAL_SAVINGS_RATE: float
    LOAN_PRIOR_DELINQUENCY: int
    LOAN_PRIOR_RECORD: int


@app.post("/predict")
def predict(application: LoanApplication):
    df = pd.DataFrame([application.model_dump()])[FEATURES]
    charge_off_probability = float(model.predict_proba(df)[0][1])
    decision = "Deny" if charge_off_probability >= THRESHOLD else "Approve"
    return {
        "decision": decision,
        "charge_off_probability": round(charge_off_probability, 4),
        "threshold": THRESHOLD,
    }
