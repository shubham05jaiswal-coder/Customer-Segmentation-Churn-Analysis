import pandas as pd
import pytest
from src.etl import clean_customers, clean_transactions, validate

def test_customer_cleaning_deduplicates():
    df = pd.DataFrame({"customer_id":["A","A"],"signup_date":["2024-01-01","2024-01-01"],"country":["IN",None],"acquisition_channel":["Web","Web"],"is_churned":[0,1]})
    out = clean_customers(df)
    assert len(out) == 1
    assert out.iloc[0]["is_churned"] == 1

def test_transaction_cleaning_removes_negative_amount():
    df = pd.DataFrame({"transaction_id":["T1","T2"],"customer_id":["A","A"],"transaction_date":["2024-01-01","2024-01-02"],"amount":[50,-2],"status":["completed","completed"]})
    assert len(clean_transactions(df)) == 1

def test_missing_columns_raise():
    with pytest.raises(ValueError):
        validate(pd.DataFrame({"x":[1]}), ["customer_id"], "test")
