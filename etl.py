from pathlib import Path
import pandas as pd
from sqlalchemy import text

CUSTOMER_COLS = ["customer_id","signup_date","country","acquisition_channel","is_churned"]
TRANSACTION_COLS = ["transaction_id","customer_id","transaction_date","amount","status"]

def read_input(path):
    path = Path(path)
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() in (".xlsx", ".xls"):
        return pd.read_excel(path)
    raise ValueError("Only CSV and Excel files are supported.")

def validate(df, required, label):
    missing = sorted(set(required) - set(df.columns))
    if missing:
        raise ValueError(f"{label} missing columns: {missing}")

def clean_customers(df):
    validate(df, CUSTOMER_COLS, "customers")
    df = df[CUSTOMER_COLS].copy()
    df["customer_id"] = df["customer_id"].astype(str).str.strip()
    df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce")
    df["country"] = df["country"].fillna("Unknown").astype(str).str.strip()
    df["acquisition_channel"] = df["acquisition_channel"].fillna("Unknown").astype(str).str.strip()
    df["is_churned"] = pd.to_numeric(df["is_churned"], errors="coerce")
    df = df.dropna(subset=["customer_id","signup_date","is_churned"])
    df["signup_date"] = df["signup_date"].dt.date
    df["is_churned"] = df["is_churned"].astype(int).clip(0, 1)
    return df.drop_duplicates("customer_id", keep="last")

def clean_transactions(df):
    validate(df, TRANSACTION_COLS, "transactions")
    df = df[TRANSACTION_COLS].copy()
    df["transaction_id"] = df["transaction_id"].astype(str).str.strip()
    df["customer_id"] = df["customer_id"].astype(str).str.strip()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["status"] = df["status"].fillna("unknown").astype(str).str.lower().str.strip()
    df = df.dropna(subset=["transaction_id","customer_id","transaction_date","amount"])
    df = df[df["amount"] >= 0]
    return df.drop_duplicates("transaction_id", keep="last")

def load_tables(engine, customers, transactions):
    with engine.begin() as conn:
        customers.to_sql("customers_stage", conn, schema="staging", if_exists="replace", index=False)
        transactions.to_sql("transactions_stage", conn, schema="staging", if_exists="replace", index=False)
        conn.execute(text("INSERT INTO raw.customers SELECT * FROM staging.customers_stage ON CONFLICT (customer_id) DO UPDATE SET signup_date=EXCLUDED.signup_date,country=EXCLUDED.country,acquisition_channel=EXCLUDED.acquisition_channel,is_churned=EXCLUDED.is_churned"))
        conn.execute(text("INSERT INTO raw.transactions SELECT * FROM staging.transactions_stage ON CONFLICT (transaction_id) DO UPDATE SET customer_id=EXCLUDED.customer_id,transaction_date=EXCLUDED.transaction_date,amount=EXCLUDED.amount,status=EXCLUDED.status"))
