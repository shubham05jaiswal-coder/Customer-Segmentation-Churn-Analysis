import logging
from pathlib import Path
from sqlalchemy import create_engine, text
from src.config import database_url, DATA_DIR
from src.etl import read_input, clean_customers, clean_transactions, load_tables
from src.modeling import build_rfm, train_churn_model

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def main():
    d = Path(DATA_DIR)
    cp = next((p for p in [d/"customers.csv", d/"customers.xlsx"] if p.exists()), None)
    tp = next((p for p in [d/"transactions.csv", d/"transactions.xlsx"] if p.exists()), None)
    if cp is None or tp is None:
        raise FileNotFoundError("Provide data/customers.csv and data/transactions.csv (or .xlsx equivalents).")
    customers, transactions = clean_customers(read_input(cp)), clean_transactions(read_input(tp))
    engine = create_engine(database_url(), pool_pre_ping=True)
    with engine.begin() as conn:
        for schema in ["raw","staging","analytics"]:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
    load_tables(engine, customers, transactions)
    rfm = build_rfm(engine)
    result = train_churn_model(rfm, engine)
    logging.info("Pipeline complete. customers=%s transactions=%s model=%s",len(customers),len(transactions),result)

if __name__ == "__main__":
    main()
