-- Module 1: Event Schema Exploration
-- Counts events by type, unique users, and unique sessions across the
-- full GA4 obfuscated ecommerce sample dataset (Nov 2020 - Jan 2021).
--
-- BigQuery-specific syntax used here (flagging per project rules):
--   1. `events_*` + `_TABLE_SUFFIX` — a wildcard table. GA4 export creates
--      ONE physical table per day (events_20201101, events_20201102, ...).
--      This syntax queries all of them in a single scan instead of writing
--      92 UNION ALL statements by hand.
--   2. `UNNEST(event_params)` — event_params is a REPEATED RECORD (an array
--      of key/value structs), not a normal column. UNNEST flattens that
--      array so we can filter for one specific key, e.g. 'ga_session_id'.

SELECT
  event_name,
  COUNT(*) AS event_count,
  COUNT(DISTINCT user_pseudo_id) AS unique_users,
  COUNT(DISTINCT CONCAT(
    user_pseudo_id, '-',
    CAST((SELECT value.int_value FROM UNNEST(event_params)
          WHERE key = 'ga_session_id') AS STRING)
  )) AS unique_sessions
FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
GROUP BY event_name
ORDER BY event_count DESC;
