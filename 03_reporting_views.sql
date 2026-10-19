CREATE OR REPLACE VIEW analytics.vw_customer_kpis AS
SELECT COUNT(*) total_customers, COUNT(*) FILTER(WHERE is_churned=1) churned_customers,
COUNT(*) FILTER(WHERE is_churned=0) active_customers,
ROUND(100.0*COUNT(*) FILTER(WHERE is_churned=1)/NULLIF(COUNT(*),0),2) churn_rate_pct FROM raw.customers;
CREATE OR REPLACE VIEW analytics.vw_monthly_revenue AS
SELECT date_trunc('month',transaction_date)::date month,
SUM(amount) FILTER(WHERE lower(status)='completed') revenue,
COUNT(*) FILTER(WHERE lower(status)='completed') completed_transactions
FROM raw.transactions GROUP BY 1;
CREATE OR REPLACE VIEW analytics.vw_segment_performance AS
SELECT segment_id,COUNT(*) customers,ROUND(AVG(recency_days),1) avg_recency_days,
ROUND(AVG(frequency),2) avg_frequency,ROUND(AVG(monetary),2) avg_customer_revenue,
ROUND(100.0*AVG(is_churned),2) churn_rate_pct FROM analytics.customer_rfm GROUP BY segment_id;
