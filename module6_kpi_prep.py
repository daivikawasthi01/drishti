"""Module 6 KPI Prep: computes header KPIs and pulls the two new BigQuery
queries the dashboard needs (monthly revenue, DAU/MAU) into local CSVs."""

from pathlib import Path

import pandas as pd
from google.cloud import bigquery

PROJECT_ID = "drishti-daivik-01"
DATA_DIR = Path("data")


def get_client():
    return bigquery.Client(project=PROJECT_ID)


def run_query(client, sql_path):
    query = Path(sql_path).read_text()
    return client.query(query).to_dataframe()


def main():
    client = get_client()

    print("Running monthly revenue query...")
    monthly_revenue = run_query(client, "queries/11_monthly_revenue.sql")
    monthly_revenue.to_csv(DATA_DIR / "monthly_revenue.csv", index=False)
    print(monthly_revenue.to_string(index=False))

    print("\nRunning DAU/MAU query...")
    dau_mau = run_query(client, "queries/12_dau_mau.sql")
    dau_mau.to_csv(DATA_DIR / "dau_mau.csv", index=False)
    print(dau_mau.to_string(index=False))

    print("\nRunning overall KPI scalars query...")
    overall = run_query(client, "queries/13_overall_kpis.sql")
    print(overall.to_string(index=False))

    # Cart abandonment and overall conversion don't need a new BigQuery call --
    # both are derivable from funnel_overall.csv, which we already computed
    # on Day 2. Reusing it instead of re-querying keeps this script cheap and
    # reinforces the "precomputed data" principle behind the whole dashboard.
    funnel = pd.read_csv(DATA_DIR / "funnel_overall.csv")
    purchase_users = funnel.loc[funnel["step"] == "Purchase", "users"].iloc[0]
    session_users = funnel.loc[funnel["step"] == "Session Start", "users"].iloc[0]
    cart_users = funnel.loc[funnel["step"] == "Add to Cart", "users"].iloc[0]

    overall_conversion_pct = round(100 * purchase_users / session_users, 2)
    cart_abandonment_pct = round(100 * (1 - purchase_users / cart_users), 2)

    monthly_revenue_sorted = monthly_revenue.sort_values("month")
    latest = monthly_revenue_sorted["total_revenue"].iloc[-1]
    previous = monthly_revenue_sorted["total_revenue"].iloc[-2]
    mom_growth_pct = round(100 * (latest - previous) / previous, 2)

    avg_dau_mau_pct = round(dau_mau["dau_mau_ratio_pct"].mean(), 2)

    kpi_summary = pd.DataFrame([{
        "total_revenue": overall["total_revenue"].iloc[0],
        "total_transactions": int(overall["total_transactions"].iloc[0]),
        "avg_order_value": overall["avg_order_value"].iloc[0],
        "overall_conversion_pct": overall_conversion_pct,
        "cart_abandonment_pct": cart_abandonment_pct,
        "mom_revenue_growth_pct": mom_growth_pct,
        "avg_dau_mau_ratio_pct": avg_dau_mau_pct,
    }])
    kpi_summary.to_csv(DATA_DIR / "kpi_summary.csv", index=False)

    print("\nHeader KPI summary:")
    print(kpi_summary.to_string(index=False))
    print("\nSaved: data/monthly_revenue.csv, data/dau_mau.csv, data/kpi_summary.csv")


if __name__ == "__main__":
    main()