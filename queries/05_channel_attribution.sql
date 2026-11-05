-- Module 3: Channel Attribution Analysis
--
-- For each traffic channel: total users, buyers, conversion rate, total
-- revenue, average order value (AOV), and repeat purchase rate.
--
-- Attribution note: `channel` here is taken from traffic_source.medium on
-- the PURCHASE event itself -- i.e. this is "last-touch" attribution (which
-- channel was the user on when they actually bought), not "first-touch"
-- (which channel originally acquired them). A user who discovered the site
-- via organic search but came back later through a paid retargeting ad
-- would be attributed to `cpc` here, not `organic`. Both are valid, widely
-- used attribution models -- this project uses last-touch for simplicity
-- and consistency with the Day 3 device/channel funnel breakdown, which
-- used the same per-event channel logic.
--
-- SAFE_DIVIDE is used instead of plain `/` wherever the denominator could
-- legitimately be zero (e.g. a channel with zero buyers) -- BigQuery raises
-- a runtime error on division by zero with `/`, while SAFE_DIVIDE returns
-- NULL instead of failing the whole query.

WITH purchases AS (
  SELECT
    user_pseudo_id,
    traffic_source.medium AS channel,
    ecommerce.purchase_revenue AS revenue
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
    AND event_name = 'purchase'
),
user_purchases AS (
  SELECT
    user_pseudo_id,
    channel,
    COUNT(*) AS purchase_count,
    SUM(revenue) AS user_revenue
  FROM purchases
  GROUP BY user_pseudo_id, channel
),
channel_totals AS (
  SELECT
    traffic_source.medium AS channel,
    COUNT(DISTINCT user_pseudo_id) AS total_users
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
  GROUP BY channel
)
SELECT
  ct.channel,
  ct.total_users,
  COUNT(DISTINCT up.user_pseudo_id) AS buyers,
  ROUND(100.0 * COUNT(DISTINCT up.user_pseudo_id) / ct.total_users, 2) AS conversion_rate_pct,
  ROUND(SUM(up.user_revenue), 2) AS total_revenue,
  ROUND(SAFE_DIVIDE(SUM(up.user_revenue), SUM(up.purchase_count)), 2) AS avg_order_value,
  ROUND(100.0 * SAFE_DIVIDE(COUNTIF(up.purchase_count > 1), COUNT(DISTINCT up.user_pseudo_id)), 2) AS repeat_purchase_rate_pct
FROM channel_totals ct
LEFT JOIN user_purchases up ON ct.channel = up.channel
GROUP BY ct.channel, ct.total_users
ORDER BY total_revenue DESC;

