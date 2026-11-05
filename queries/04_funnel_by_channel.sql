-- Module 2 (Part 2): 6-step purchase funnel broken down by traffic channel
--
-- Same pattern again, grouped by traffic_source.medium instead of device --
-- this is the acquisition channel (organic, cpc, direct, referral, email,
-- etc.), so this table answers "which channels bring users who actually
-- convert," as opposed to just "which channels bring the most traffic."

WITH user_channel_funnel AS (
  SELECT
    user_pseudo_id,
    traffic_source.medium AS channel,
    MAX(IF(event_name = 'session_start', 1, 0)) AS did_session_start,
    MAX(IF(event_name = 'view_item', 1, 0)) AS did_view_item,
    MAX(IF(event_name = 'add_to_cart', 1, 0)) AS did_add_to_cart,
    MAX(IF(event_name = 'begin_checkout', 1, 0)) AS did_begin_checkout,
    MAX(IF(event_name = 'add_payment_info', 1, 0)) AS did_add_payment_info,
    MAX(IF(event_name = 'purchase', 1, 0)) AS did_purchase
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
  GROUP BY user_pseudo_id, channel
)
SELECT
  channel,
  SUM(did_session_start) AS session_start,
  SUM(did_view_item) AS view_item,
  SUM(did_add_to_cart) AS add_to_cart,
  SUM(did_begin_checkout) AS begin_checkout,
  SUM(did_add_payment_info) AS add_payment_info,
  SUM(did_purchase) AS purchase
FROM user_channel_funnel
GROUP BY channel
ORDER BY session_start DESC;