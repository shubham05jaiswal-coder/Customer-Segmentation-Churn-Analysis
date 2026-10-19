CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE TABLE IF NOT EXISTS raw.customers (
 customer_id VARCHAR(64) PRIMARY KEY, signup_date DATE NOT NULL, country TEXT NOT NULL DEFAULT 'Unknown',
 acquisition_channel TEXT NOT NULL DEFAULT 'Unknown', is_churned SMALLINT NOT NULL CHECK (is_churned IN (0,1)));
CREATE TABLE IF NOT EXISTS raw.transactions (
 transaction_id VARCHAR(64) PRIMARY KEY, customer_id VARCHAR(64) NOT NULL REFERENCES raw.customers(customer_id) DEFERRABLE INITIALLY DEFERRED,
 transaction_date TIMESTAMP NOT NULL, amount NUMERIC(14,2) NOT NULL CHECK (amount>=0), status TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS analytics.customer_rfm (
 customer_id VARCHAR(64) PRIMARY KEY, recency_days INTEGER NOT NULL, frequency INTEGER NOT NULL, monetary NUMERIC(14,2) NOT NULL,
 is_churned SMALLINT NOT NULL, signup_date DATE, country TEXT, acquisition_channel TEXT, segment_id INTEGER NOT NULL,
 refreshed_at TIMESTAMPTZ NOT NULL DEFAULT NOW());
CREATE TABLE IF NOT EXISTS analytics.customer_segments (
 segment_id INTEGER PRIMARY KEY, customer_count INTEGER NOT NULL, avg_recency_days NUMERIC, avg_frequency NUMERIC,
 avg_monetary NUMERIC, refreshed_at TIMESTAMPTZ NOT NULL DEFAULT NOW());
CREATE TABLE IF NOT EXISTS analytics.churn_predictions (
 customer_id VARCHAR(64) PRIMARY KEY, churn_probability NUMERIC(8,6) NOT NULL, risk_band TEXT NOT NULL,
 refreshed_at TIMESTAMPTZ NOT NULL DEFAULT NOW());
CREATE INDEX IF NOT EXISTS ix_transactions_customer_date ON raw.transactions(customer_id,transaction_date);
