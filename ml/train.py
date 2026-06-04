import os
import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import joblib

load_dotenv()

OUTPUT_DIR = os.getenv("MODEL_OUTPUT_DIR", "/artifacts")
os.makedirs(OUTPUT_DIR, exist_ok=True)

conn = snowflake.connector.connect(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA_TRANSFORMED"),
)

query = """
    SELECT *
    FROM FACT_LOANS l
    LEFT JOIN DIM_FRED_MACRO_INDICATORS f
    ON l.LOAN_ISSUE_DATE = f.DATE
"""

cursor = conn.cursor()
cursor.execute(query)
cols = [desc[0] for desc in cursor.description]
df = pd.DataFrame(cursor.fetchall(), columns=cols)
cursor.close()
conn.close()

# Create Target Variable
df = df[df["LOAN_STATUS"].isin(["Fully Paid", "Charged Off"])].copy()
df["TARGET"] = (df["LOAN_STATUS"] == "Charged Off").astype(int)  # Charged Off = 1, Fully Paid = 0

# Missing Value Analysis/Handling
df["LOAN_PRIOR_DELINQUENCY"] = df["LOAN_MTHS_SINCE_LAST_DELINQ"].notnull().astype(int)
df["LOAN_PRIOR_RECORD"] = df["LOAN_MTHS_SINCE_LAST_RECORD"].notnull().astype(int)
df = df[df["LOAN_DTI"].notnull()]

zero_fill_cols = [
    "LOAN_EMP_LENGTH", "LOAN_TOTAL_REV_HI_LIM", "LOAN_TOT_COLL_AMT",
    "LOAN_NUM_ACCTS_EVER_120_PD", "LOAN_MORT_ACC",
]
df[zero_fill_cols] = df[zero_fill_cols].fillna(0)

median_fill_cols = [
    "LOAN_TOT_CUR_BAL", "LOAN_TOT_HI_CRED_LIM", "LOAN_TOTAL_BAL_EX_MORT",
    "LOAN_TOTAL_BC_LIMIT", "LOAN_AVG_CUR_BAL", "LOAN_BC_UTIL",
    "LOAN_BC_OPEN_TO_BUY", "LOAN_PERCENT_BC_GT_75", "LOAN_PCT_TL_NVR_DLQ",
]
df[median_fill_cols] = df[median_fill_cols].fillna(df[median_fill_cols].median())

df = df.drop(columns=[
    "LOAN_MTHS_SINCE_LAST_DELINQ", "LOAN_MTHS_SINCE_LAST_RECORD",
    "LOAN_REVOL_UTIL", "LOAN_PUB_REC_BANKRUPTCIES",
])

# Drop Columns Without Predictive Value
df = df.drop(columns=["LOAN_ID", "LOAN_STATUS", "LOAN_ISSUE_DATE", "LOAN_ADDR_STATE", "DATE"])

# Convert To Numeric Values
df["LOAN_TERM"] = df["LOAN_TERM"].str.split().str[0].astype(int)
df["LOAN_PURPOSE"] = (df["LOAN_PURPOSE"] == "debt_consolidation").astype(int)
df["LOAN_EMP_LENGTH"] = (
    df["LOAN_EMP_LENGTH"].astype(str).str.replace(r"[<>+]|years?", "", regex=True).str.strip().astype(int)
)
df["LOAN_HOME_OWNERSHIP"] = (df["LOAN_HOME_OWNERSHIP"] == "OWN").astype(int)
df["LOAN_APPLICATION_TYPE"] = (df["LOAN_APPLICATION_TYPE"] == "Individual").astype(int)
df["LOAN_EARLIEST_CR_LINE"] = df["LOAN_EARLIEST_CR_LINE"].str.split("-").str[1].astype(int)

df = df.rename(columns={
    "LOAN_TERM": "LOAN_TERM_MONTHS",
    "LOAN_PURPOSE": "LOAN_PURPOSE_IS_DEBT_CONSOLIDATION",
    "LOAN_HOME_OWNERSHIP": "LOAN_OWNS_HOME",
    "LOAN_APPLICATION_TYPE": "LOAN_APPLYING_AS_INDIVIDUAL",
})

# Drop Redundant Correlated Variables, Or Variables Not Correlated With TARGET
df = df.drop(columns=[
    "LOAN_INSTALLMENT", "LOAN_FICO_RANGE_HIGH", "LOAN_TOT_CUR_BAL", "LOAN_AVG_CUR_BAL",
    "LOAN_BC_OPEN_TO_BUY", "LOAN_PERCENT_BC_GT_75", "LOAN_PCT_TL_NVR_DLQ",
    "UNEMPLOYMENT_RATE", "CONSUMER_PRICE_INDEX", "LOAN_PUB_REC", "LOAN_TOTAL_ACC",
    "LOAN_REVOL_BAL", "LOAN_TOTAL_REV_HI_LIM",
])

# To Simplify User Input, Exclude Non-FRED features with Importance < .01
features = [
    "LOAN_AMOUNT", "LOAN_TERM_MONTHS", "LOAN_INTEREST_RATE",
    "LOAN_PURPOSE_IS_DEBT_CONSOLIDATION", "LOAN_EMP_LENGTH", "LOAN_OWNS_HOME",
    "LOAN_ANNUAL_INCOME", "LOAN_APPLYING_AS_INDIVIDUAL", "LOAN_DTI",
    "LOAN_FICO_RANGE_LOW", "LOAN_EARLIEST_CR_LINE", "LOAN_OPEN_ACC",
    "LOAN_DELINQ_2YRS", "LOAN_INQ_LAST_6MTHS", "LOAN_TOT_HI_CRED_LIM",
    "LOAN_TOTAL_BC_LIMIT", "LOAN_MORT_ACC", "LOAN_BC_UTIL", "GDP",
    "FEDERAL_FUNDS_RATE", "FIXED_MORTGAGE_RATE", "PERSONAL_SAVINGS_RATE",
    "LOAN_PRIOR_DELINQUENCY", "LOAN_PRIOR_RECORD",
]

# Train Model
X = df[features].fillna(-1)
y = df["TARGET"]

X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.1, random_state=42, stratify=y)
X_train, X_eval, y_train, y_eval = train_test_split(X_temp, y_temp, test_size=0.15, random_state=42, stratify=y_temp)

model = xgb.XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.1,
    scale_pos_weight=(y_train == 0).sum() / (y_train == 1).sum(),
    random_state=42,
    n_jobs=-1,
    eval_metric="auc",
)

model.fit(X_train, y_train, eval_set=[(X_eval, y_eval)], verbose=50)

# Model Evaluation
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

print(classification_report(y_test, y_pred))
print(f"ROC AUC: {roc_auc_score(y_test, y_prob):.4f}")

# A threshold of 0.6 establishes that a loan must be predicted >= 60 percent likely to charge off to deny
# This minimizes false negatives (Accepting a loan that gets charged off, which is costly) without an unreasonable amount
# of false positives (Denying a loan that would have been fully paid)

# Save Model
#joblib.dump(model, os.path.join(OUTPUT_DIR, "model.pkl"))
#joblib.dump({"threshold": 0.6, "features": features}, os.path.join(OUTPUT_DIR, "model_config.pkl"))
#print(f"Model saved to {OUTPUT_DIR}")
