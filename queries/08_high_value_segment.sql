-- Module 5 Part A: High-Value Segment (Top 20% by Spend) vs Everyone Else
--
-- NTILE(5) splits BUYERS into 5 equal-sized buckets ordered by total spend,
-- descending -- bucket 1 is the top 20% of spenders. This answers "how
-- concentrated is our revenue" (the classic 80/20 check), not just "who
-- are our biggest spenders."

WITH user_revenue AS (
  SELECT
    user_pseudo_id,
    COUNT(*) AS purchase_count,
    SUM(ecommerce.purchase_revenue) AS total_spend
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
    AND event_name = 'purchase'
  GROUP BY user_pseudo_id
),
ranked AS (
  SELECT
    *,
    NTILE(5) OVER (ORDER BY total_spend DESC) AS spend_bucket
  FROM user_revenue
)
SELECT
  IF(spend_bucket = 1, 'top_20_pct', 'remaining_80_pct') AS segment,
  COUNT(*) AS buyers,
  ROUND(SUM(total_spend), 2) AS total_revenue,
  ROUND(AVG(total_spend), 2) AS avg_revenue_per_buyer,
  ROUND(AVG(purchase_count), 2) AS avg_purchase_count
FROM ranked
GROUP BY segment
ORDER BY segment DESC;