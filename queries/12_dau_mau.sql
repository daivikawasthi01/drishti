-- Module 6: DAU/MAU Stickiness Ratio, computed per month
--
-- DAU/MAU is a standard product-health metric: average daily active users
-- divided by monthly active users, as a percentage. A high ratio means
-- people who use the product in a given month tend to come back on many
-- different days that month (sticky); a low ratio means most of a month's
-- users only show up once or twice.

WITH daily_users AS (
  SELECT
    PARSE_DATE('%Y%m%d', event_date) AS activity_date,
    DATE_TRUNC(PARSE_DATE('%Y%m%d', event_date), MONTH) AS month,
    COUNT(DISTINCT user_pseudo_id) AS dau
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
  GROUP BY activity_date, month
),
monthly_users AS (
  SELECT
    DATE_TRUNC(PARSE_DATE('%Y%m%d', event_date), MONTH) AS month,
    COUNT(DISTINCT user_pseudo_id) AS mau
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
  GROUP BY month
)
SELECT
  d.month,
  ROUND(AVG(d.dau), 0) AS avg_dau,
  m.mau,
  ROUND(100.0 * AVG(d.dau) / m.mau, 2) AS dau_mau_ratio_pct
FROM daily_users d
JOIN monthly_users m USING (month)
GROUP BY d.month, m.mau
ORDER BY d.month;