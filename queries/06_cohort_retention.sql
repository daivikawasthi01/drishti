-- Module 4: Cohort Retention Analysis
--
-- Groups users by the MONTH of their first purchase ("cohort_month"), then
-- measures what % of that cohort purchased again in each subsequent month
-- (months_since_first = 0, 1, 2, ...). This answers "is the product
-- sticky" -- not just "did we get a sale," but "do people come back."
--
-- cohort_size is computed separately from active_users on purpose: cohort
-- size is fixed per cohort (how many people first bought in that month,
-- period), while active_users varies by months_since_first (how many of
-- them were ALSO active N months later). Computing both from the same
-- grouped query would incorrectly tie cohort_size to each month bucket
-- instead of the cohort as a whole.
--
-- Note: our date range (Nov 2020 - Jan 2021) only supports 3 cohort months
-- and a maximum of 2 months of "since first" tracking (the Jan cohort has
-- no later months to look ahead into) -- a real constraint of a 92-day
-- dataset, not a bug. With a full year of data this would extend further.

WITH first_purchase AS (
  SELECT
    user_pseudo_id,
    DATE_TRUNC(MIN(PARSE_DATE('%Y%m%d', event_date)), MONTH) AS cohort_month
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
    AND event_name = 'purchase'
  GROUP BY user_pseudo_id
),
cohort_sizes AS (
  SELECT cohort_month, COUNT(DISTINCT user_pseudo_id) AS cohort_size
  FROM first_purchase
  GROUP BY cohort_month
),
all_purchases AS (
  SELECT DISTINCT
    user_pseudo_id,
    DATE_TRUNC(PARSE_DATE('%Y%m%d', event_date), MONTH) AS purchase_month
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
    AND event_name = 'purchase'
),
cohort_activity AS (
  SELECT
    fp.cohort_month,
    DATE_DIFF(ap.purchase_month, fp.cohort_month, MONTH) AS months_since_first,
    COUNT(DISTINCT ap.user_pseudo_id) AS active_users
  FROM first_purchase fp
  JOIN all_purchases ap USING (user_pseudo_id)
  GROUP BY 1, 2
)
SELECT
  ca.cohort_month,
  ca.months_since_first,
  cs.cohort_size,
  ca.active_users,
  ROUND(100.0 * ca.active_users / cs.cohort_size, 2) AS retention_pct
FROM cohort_activity ca
JOIN cohort_sizes cs USING (cohort_month)
ORDER BY 1, 2;

