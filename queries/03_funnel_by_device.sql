-- Module 2 (Part 2): 6-step purchase funnel broken down by device category
--
-- Same conditional-aggregation pattern as queries/02_funnel_overall.sql, but
-- now grouped by device.category as well as user_pseudo_id. A user who was
-- active on more than one device type contributes to each device's totals
-- separately -- that's intentional: we're asking "how does mobile perform
-- as a funnel" not "how many humans own multiple devices."
--
-- device.category is a plain STRUCT field (not REPEATED), so it's read with
-- direct dot notation -- no UNNEST needed (see docs/blueprint schema notes
-- from Day 1 on REPEATED vs plain RECORD fields).

WITH user_device_funnel AS (
  SELECT
    user_pseudo_id,
    device.category AS device,
    MAX(IF(event_name = 'session_start', 1, 0)) AS did_session_start,
    MAX(IF(event_name = 'view_item', 1, 0)) AS did_view_item,
    MAX(IF(event_name = 'add_to_cart', 1, 0)) AS did_add_to_cart,
    MAX(IF(event_name = 'begin_checkout', 1, 0)) AS did_begin_checkout,
    MAX(IF(event_name = 'add_payment_info', 1, 0)) AS did_add_payment_info,
    MAX(IF(event_name = 'purchase', 1, 0)) AS did_purchase
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
  GROUP BY user_pseudo_id, device
)
SELECT
  device,
  SUM(did_session_start) AS session_start,
  SUM(did_view_item) AS view_item,
  SUM(did_add_to_cart) AS add_to_cart,
  SUM(did_begin_checkout) AS begin_checkout,
  SUM(did_add_payment_info) AS add_payment_info,
  SUM(did_purchase) AS purchase
FROM user_device_funnel
GROUP BY device
ORDER BY session_start DESC;