-- Module 5 Part B: Organic vs Paid (cpc) Conversion -- Chi-Square Input
--
-- Builds the 2x2 contingency table directly in SQL: for each channel,
-- how many users converted (purchased) vs did not. Doing this aggregation
-- in BigQuery rather than pulling every user row into Python keeps the
-- data transferred down to 2 rows instead of ~127K individual users.

WITH user_channel AS (
  SELECT
    user_pseudo_id,
    traffic_source.medium AS channel,
    MAX(IF(event_name = 'purchase', 1, 0)) AS converted
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
    AND traffic_source.medium IN ('organic', 'cpc')
  GROUP BY user_pseudo_id, channel
)
SELECT
  channel,
  SUM(converted) AS converted_users,
  SUM(1 - converted) AS not_converted_users
FROM user_channel
GROUP BY channel;