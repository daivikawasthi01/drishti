-- Module 5 Part A: New vs Returning Users
--
-- "New" = the user's first_visit event happened inside our date range --
-- meaning this window IS the start of their relationship with the site.
-- "Returning" = active in our range, but no first_visit event in-range,
-- meaning they'd already visited before Nov 1, 2020 (first_visit fires
-- exactly once per user, ever, so its absence here means it happened
-- earlier, outside what we can see).

WITH user_type AS (
  SELECT
    user_pseudo_id,
    MAX(IF(event_name = 'first_visit', 1, 0)) AS is_new
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
  GROUP BY user_pseudo_id
),
user_purchases AS (
  SELECT
    user_pseudo_id,
    COUNT(*) AS purchase_count,
    SUM(ecommerce.purchase_revenue) AS user_revenue
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
    AND event_name = 'purchase'
  GROUP BY user_pseudo_id
)
SELECT
  IF(ut.is_new = 1, 'new', 'returning') AS user_type,
  COUNT(DISTINCT ut.user_pseudo_id) AS total_users,
  COUNT(DISTINCT up.user_pseudo_id) AS buyers,
  ROUND(100.0 * COUNT(DISTINCT up.user_pseudo_id) / COUNT(DISTINCT ut.user_pseudo_id), 2) AS conversion_rate_pct,
  ROUND(SUM(up.user_revenue), 2) AS total_revenue,
  ROUND(SAFE_DIVIDE(SUM(up.user_revenue), COUNT(DISTINCT up.user_pseudo_id)), 2) AS avg_revenue_per_buyer
FROM user_type ut
LEFT JOIN user_purchases up USING (user_pseudo_id)
GROUP BY user_type
ORDER BY user_type;