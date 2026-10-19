-- Data quality checks: ideally return zero rows.
SELECT t.* FROM raw.transactions t LEFT JOIN raw.customers c USING(customer_id) WHERE c.customer_id IS NULL;
SELECT transaction_id, COUNT(*) FROM raw.transactions GROUP BY transaction_id HAVING COUNT(*)>1;
SELECT date_trunc('month',transaction_date)::date AS month, lower(status) AS status, SUM(amount) AS amount
FROM raw.transactions GROUP BY 1,2 ORDER BY 1,2;
