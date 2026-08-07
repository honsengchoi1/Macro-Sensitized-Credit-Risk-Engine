SELECT 
    v.fico_tier, 
    ROUND(AVG(p.npl_ratio), 4) AS average_npl
FROM portfolio_monthly_performance p
JOIN internal_loan_vintages v ON p.cohort_id = v.cohort_id
GROUP BY v.fico_tier;

SELECT 
    v.interest_rate_type, 
    CASE WHEN p.reporting_date >= '2022-06-01' THEN '2_Post-Shock' ELSE '1_Pre-Shock' END AS time_period,
    ROUND(AVG(p.npl_ratio), 4) AS average_npl
FROM portfolio_monthly_performance p
JOIN internal_loan_vintages v ON p.cohort_id = v.cohort_id
GROUP BY v.interest_rate_type, time_period
ORDER BY v.interest_rate_type, time_period;

SELECT 
    (SELECT COUNT(*) FROM internal_loan_vintages) AS total_cohorts,
    (SELECT COUNT(*) FROM portfolio_monthly_performance) AS total_records;