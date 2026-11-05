-- Module 6: Monthly Revenue Trend (feeds Month-over-Month growth KPI)

SELECT
  DATE_TRUNC(PARSE_DATE('%Y%m%d', event_date), MONTH) AS month,
  ROUND(SUM(ecommerce.purchase_revenue), 2) AS total_revenue
FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
  AND event_name = 'purchase'
GROUP BY month
ORDER BY month;