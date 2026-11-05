-- Module 6: Overall KPI scalars -- total revenue, transaction count, AOV
-- Kept separate from queries/05_channel_attribution.sql because that one
-- is grouped by channel; this is the single company-wide number, which is
-- what the dashboard's header KPI row actually needs.

SELECT
  COUNT(*) AS total_transactions,
  ROUND(SUM(ecommerce.purchase_revenue), 2) AS total_revenue,
  ROUND(AVG(ecommerce.purchase_revenue), 2) AS avg_order_value
FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
  AND event_name = 'purchase';