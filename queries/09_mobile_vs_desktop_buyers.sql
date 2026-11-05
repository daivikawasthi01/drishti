-- Module 5 Part A: Mobile vs Desktop Buyers -- AOV and Purchase Frequency
--
-- Restricted to users who made at least one purchase (buyers only) --
-- different question from Day 3's device funnel, which covered ALL
-- visitors. This asks "among people who already bought, does device
-- correlate with how much or how often they buy."

WITH buyer_device AS (
  SELECT
    user_pseudo_id,
    device.category AS device,
    COUNT(*) AS purchase_count,
    SUM(ecommerce.purchase_revenue) AS total_spend
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
    AND event_name = 'purchase'
  GROUP BY user_pseudo_id, device
)
SELECT
  device,
  COUNT(*) AS buyers,
  ROUND(SUM(total_spend), 2) AS total_revenue,
  ROUND(SAFE_DIVIDE(SUM(total_spend), SUM(purchase_count)), 2) AS avg_order_value,
  ROUND(AVG(purchase_count), 2) AS avg_purchase_frequency
FROM buyer_device
GROUP BY device
ORDER BY total_revenue DESC;