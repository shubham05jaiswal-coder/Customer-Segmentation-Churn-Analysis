from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sqlalchemy import text
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, precision_score, recall_score

def build_rfm(engine):
    query = """WITH t AS (
      SELECT * FROM raw.transactions WHERE lower(status)='completed'
    ), anchor AS (SELECT COALESCE(MAX(transaction_date)::date,CURRENT_DATE) d FROM t)
    SELECT c.customer_id,
      COALESCE((a.d-MAX(t.transaction_date)::date),9999)::int recency_days,
      COUNT(t.transaction_id)::int frequency, COALESCE(SUM(t.amount),0)::numeric(14,2) monetary,
      c.is_churned,c.signup_date,c.country,c.acquisition_channel
    FROM raw.customers c CROSS JOIN anchor a LEFT JOIN t ON t.customer_id=c.customer_id
    GROUP BY c.customer_id,a.d,c.is_churned,c.signup_date,c.country,c.acquisition_channel"""
    df = pd.read_sql(query, engine)
    if df.empty: return df
    x = np.log1p(df[["recency_days","frequency","monetary"]].astype(float).clip(lower=0))
    if len(df) >= 4 and x.nunique().min() > 1:
        k = min(4, max(2, int(np.sqrt(len(df)/2))), len(df))
        df["segment_id"] = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(StandardScaler().fit_transform(x))
    else:
        df["segment_id"] = 0
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE analytics.customer_rfm"))
        df[["customer_id","recency_days","frequency","monetary","is_churned","signup_date","country","acquisition_channel","segment_id"]].to_sql("customer_rfm", conn, schema="analytics", if_exists="append", index=False)
        conn.execute(text("TRUNCATE analytics.customer_segments"))
        conn.execute(text("INSERT INTO analytics.customer_segments SELECT segment_id,COUNT(*),AVG(recency_days),AVG(frequency),AVG(monetary),NOW() FROM analytics.customer_rfm GROUP BY segment_id"))
    return df

def train_churn_model(df, engine, output_dir="artifacts"):
    if df.empty or len(df) < 20 or df["is_churned"].nunique() < 2:
        return {"status":"skipped", "reason":"Need at least 20 customers and both churn classes."}
    X = df[["recency_days","frequency","monetary"]].astype(float).clip(lower=0)
    X["frequency"] = np.log1p(X["frequency"])
    X["monetary"] = np.log1p(X["monetary"])
    y = df["is_churned"].astype(int)
    Xtr, Xte, ytr, yte = train_test_split(X,y,test_size=.25,random_state=42,stratify=y)
    model = Pipeline([("imputer",SimpleImputer(strategy="median")),("scale",StandardScaler()),("clf",LogisticRegression(max_iter=1000,class_weight="balanced"))])
    model.fit(Xtr,ytr)
    prob = model.predict_proba(Xte)[:,1]
    metrics = {"roc_auc":float(roc_auc_score(yte,prob)), "precision":float(precision_score(yte,prob>=.5,zero_division=0)), "recall":float(recall_score(yte,prob>=.5,zero_division=0))}
    Path(output_dir).mkdir(exist_ok=True)
    joblib.dump(model, Path(output_dir)/"churn_model.joblib")
    all_prob = model.predict_proba(X)[:,1]
    pred = pd.DataFrame({"customer_id":df["customer_id"],"churn_probability":all_prob})
    pred["risk_band"] = pd.cut(pred["churn_probability"],[-.001,.33,.66,1.0],labels=["Low","Medium","High"]).astype(str)
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE analytics.churn_predictions"))
        pred.to_sql("churn_predictions",conn,schema="analytics",if_exists="append",index=False)
    return {"status":"trained","metrics":metrics}
