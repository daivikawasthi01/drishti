# Drishti — GA4 Product Analytics Dashboard

[![Live Dashboard](https://img.shields.io/badge/Live%20Dashboard-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://drishti-hznyztjuvl4r4usdcwfqg9.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![BigQuery](https://img.shields.io/badge/BigQuery-Standard%20SQL-4285F4?style=flat-square&logo=googlecloud&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-interactive%20charts-3F4F75?style=flat-square&logo=plotly&logoColor=white)

An end-to-end product analytics project built on Google's real (obfuscated) GA4 e-commerce
event data in BigQuery — a full purchase funnel, channel attribution, cohort retention,
customer segmentation with a statistical significance test, and a live executive dashboard.
Built to answer the question a growth-stage e-commerce company actually asks: *where are we
losing customers, and what should we fix first?*

| | | | |
|---|---|---|---|
| **270K** users | **4.3M** events | **109** countries | **92** days analyzed |

## The Business Question

Revenue growth has slowed. Millions of real user events sit in a database. This project
answers five things from that data alone:

1. Where do users drop out of the purchase funnel, and does device or channel make it worse?
2. Which acquisition channels bring customers who actually come back and buy again?
3. Are customers acquired months ago still active, or have they churned?
4. Who are the most valuable customers, and what do they do differently?
5. Given all of the above, what should the product team fix first?

## Dataset

- **Source:** `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*` — Google's public,
  obfuscated GA4 export from the Google Merchandise Store
- **Date range:** 2020-11-01 to 2021-01-31 (92 days)
- **Scale:** ~270,000 unique users, ~4.3 million events, 109 countries
- **Access:** free BigQuery public dataset, queried under a personal GCP project on the
  no-billing "sandbox" tier (1TB/month free query processing, no credit card required)

### Why the schema isn't a flat table

GA4 stores **one row per event**, with several fields as nested/repeated structures rather
than plain columns:

| Field | Type | Holds |
|---|---|---|
| `event_params` | REPEATED RECORD | Event-specific key/value pairs (page title, item ID, etc.) |
| `user_properties` | REPEATED RECORD | User-level attributes |
| `items` | REPEATED RECORD | Every product involved in that event |
| `device`, `geo`, `traffic_source`, `ecommerce` | RECORD (single, not repeated) | Fixed-shape nested objects |

A REPEATED field can hold a variable number of entries per row, so reading one specific value
out of it requires flattening it first:

```sql
(SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'page_title') AS page_title
```

Plain RECORD fields (`device`, `geo`, etc.) don't need this — they're one fixed object per row,
so `device.category` works directly with dot notation. This distinction — array vs. fixed
object — drives every query in this project.

## Key Findings

**Funnel (267,116 sessions → 4,419 purchases, 1.65% overall conversion):** the sharpest drop
isn't at checkout — it's at the top. Only 22.93% of visitors ever click into a product, and
only 20.48% of those add it to cart. Everything from checkout onward converts at 60-77% per
step. **The biggest leverage point is product discovery/engagement, not checkout friction.**

**Device:** mobile (1.71%) slightly outconverts desktop (1.62%) and tablet (1.57%) overall —
counter to the usual assumption that mobile underperforms. Among buyers specifically, though,
device barely affects order value or purchase frequency — it predicts *whether* someone
converts, not how valuable they are once they do.

**Channel attribution:** `cpc` (paid search) is the weakest channel on every metric — 0.98%
conversion, $54.55 average order value, 8.55% repeat purchase rate, lowest total revenue of any
channel — despite being the one channel with a direct acquisition cost. Referral performs best
per-user (1.85% conversion, $66.39 AOV, 14.62% repeat rate); organic drives the most total
revenue on volume. A chi-square test confirms the organic-vs-paid conversion gap is
statistically significant (χ² = 4.55, p = 0.033).

**Retention:** low. Only 6.4% of November's first-time buyers purchased again in December,
and just 0.91% were still active by January. December's cohort did similarly poorly (2.4%
returned in January). Most customers here are one-time buyers.

**Segmentation:** returning users convert at ~5x the rate of new users (7.07% vs. 1.36%) and
spend more per purchase ($96.14 vs. $78.29) — the retention problem above is hiding a highly
valuable segment that mostly isn't being retained. Separately, the top 20% of buyers generate
56.5% of total buyer revenue ($204,744 of $362,165) and purchase more often.

## Recommendations

Top three priorities, in order: (1) fix product-discovery/browsing UX before touching
checkout — that's where the real drop-off is, (2) reallocate `cpc` budget toward
referral/organic, since paid search underperforms every free channel, (3) build a retention
program targeting first-time buyers and the top-20% segment specifically, since returning
users convert ~5x better and a fifth of buyers drive over half of revenue.

## Dashboard

A Streamlit executive dashboard ties everything together — 6 tabs (Overview, Funnel, Retention,
Channels, Segments, Recommendations), header KPIs, fully interactive (Plotly), and reads only
precomputed CSVs — no live BigQuery connection, so it runs fast and free.

To run it locally instead:

```bash
streamlit run app.py
```

## Repo Structure

```
drishti/
├── queries/              # All SQL, numbered in build order (01-13)
├── data/                 # Precomputed CSVs + chart PNGs feeding the dashboard
├── module1_explore.py    # Day 1: schema exploration
├── module2_funnel.py     # Day 2: overall funnel
├── module2_funnel_breakdown.py  # Day 3: funnel by device/channel
├── module3_channel.py    # Day 4: channel attribution
├── module4_cohort.py     # Day 4: cohort retention
├── module5_segments.py   # Day 5: segmentation + chi-square test
├── module6_kpi_prep.py   # Day 6: dashboard KPI prep
├── app.py                # Day 6: Streamlit dashboard
└── requirements.txt
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
gcloud auth application-default login
```

## Tech Stack

BigQuery (Standard SQL), Python, pandas, matplotlib, Seaborn, Plotly, SciPy, Streamlit.

**A deliberate trade-off throughout:** all dashboard data is precomputed and saved as CSVs
rather than the dashboard holding a live BigQuery connection. That keeps the dashboard fast,
free to demo repeatedly, and reproducible — at the cost of the numbers being "as of the last
script run" rather than real-time. For a live production system this would flip; for an
analysis-and-demo project, precomputed is the right call.

## Credits

Original analysis and dashboard by [Arpita Goyal](https://github.com/arpitagoyal29/drishti). This copy is maintained with her permission.
