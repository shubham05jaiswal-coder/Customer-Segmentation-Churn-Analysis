# Customer Segmentation & Churn Analysis

Portfolio project using PostgreSQL, Python, scikit-learn, and Power BI. Includes sample CSV data, ETL, RFM features, K-Means segmentation, a churn-risk baseline model, SQL views, DAX measures, and tests.

**Important:** Sample data is synthetic. The “15% retention improvement” should be described as a business target/hypothesis unless validated by a real retention experiment.

## Architecture
CSV/Excel → Python validation and ETL → PostgreSQL raw/staging/analytics schemas → RFM + K-Means + churn model → Power BI.

## Structure
- `data/`: sample customers and transactions
- `sql/`: schema, quality checks, reporting views
- `src/`: configuration, ETL, modeling, pipeline runner
- `powerbi/measures.dax`: starter measures
- `tests/`: ETL validation tests

## Setup (Windows PowerShell)
1. Install Python 3.10+ and PostgreSQL 14+.
2. Create database: `CREATE DATABASE customer_analytics;`
3. Run `sql/01_schema.sql`, then `sql/03_reporting_views.sql` using pgAdmin or `psql`.
4. Copy `.env.example` to `.env` and update credentials.
5. Run:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python -m src.run_pipeline
   pytest
   ```
6. In Power BI Desktop, connect to PostgreSQL database `localhost:5432`, database `customer_analytics`. Import `analytics.customer_rfm`, `analytics.customer_segments`, `analytics.churn_predictions`, and `analytics.vw_monthly_revenue`.

## Data
`customers.csv`: customer_id, signup_date, country, acquisition_channel, is_churned (synthetic label).
`transactions.csv`: transaction_id, customer_id, transaction_date, amount, status.

## Modeling notes
- RFM uses completed transactions only: recency in days, purchase frequency, and monetary value.
- K-Means cluster IDs are arbitrary; interpret them using segment-level averages.
- The churn model is a baseline demonstration. For real use, define churn carefully, avoid leakage, use time-based validation, and monitor precision/recall and ROC-AUC.
- To claim a 15% retention lift, run a controlled campaign/holdout test and measure outcomes over a predefined window.

## GitHub description
Customer segmentation and churn analytics using PostgreSQL, Python, RFM analysis, K-Means clustering, churn-risk modeling, and Power BI. Includes reproducible ETL, sample data, SQL reporting views, DAX measures, and tests.

## Important
The project is packaged with synthetic data and implementation code. Run it against your PostgreSQL installation and validate the pipeline before presenting results. The claimed 15% retention improvement should be treated as a target until demonstrated with real business data and a measured retention experiment.

## Suggested topics
`customer-segmentation` `churn-analysis` `postgresql` `python` `scikit-learn` `power-bi` `etl` `rfm-analysis`
