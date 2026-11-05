-- Module 2 (Part 1): Overall 6-step purchase funnel
--
-- For each user, flag (1/0) whether they EVER triggered each funnel event
-- anywhere in the date range, then sum those flags to get step-level totals.
-- This is "conditional aggregation" — one pass over the table computes all
-- 6 steps at once, instead of 6 separate COUNT(DISTINCT ...) WHERE queries
-- (which would each re-scan the full table) or a self-join (which would
-- blow up into a cross-product of every event against every other event,
-- per user).
--
-- BigQuery-specific syntax used here:
--   - `events_*` + `_TABLE_SUFFIX`: wildcard table across all daily shards
--     (see queries/01_event_overview.sql for the same pattern)
--   - `MAX(IF(condition, 1, 0))`: per user, this returns 1 if that condition
--     was true for ANY of their event rows, 0 otherwise — collapsing
--     potentially hundreds of event rows per user into a single flag.

WITH user_funnel AS (
  SELECT
    user_pseudo_id,
    MAX(IF(event_name = 'session_start', 1, 0)) AS did_session_start,
    MAX(IF(event_name = 'view_item', 1, 0)) AS did_view_item,
    MAX(IF(event_name = 'add_to_cart', 1, 0)) AS did_add_to_cart,
    MAX(IF(event_name = 'begin_checkout', 1, 0)) AS did_begin_checkout,
    MAX(IF(event_name = 'add_payment_info', 1, 0)) AS did_add_payment_info,
    MAX(IF(event_name = 'purchase', 1, 0)) AS did_purchase
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
  GROUP BY user_pseudo_id
)
SELECT
  SUM(did_session_start) AS session_start,
  SUM(did_view_item) AS view_item,
  SUM(did_add_to_cart) AS add_to_cart,
  SUM(did_begin_checkout) AS begin_checkout,
  SUM(did_add_payment_info) AS add_payment_info,
  SUM(did_purchase) AS purchase
FROM user_funnel;