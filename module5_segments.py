"""Module 5: Customer Segmentation + Chi-Square A/B Channel Comparison."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from google.cloud import bigquery
from scipy.stats import chi2_contingency

PROJECT_ID = "drishti-daivik-01"

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


def get_client():
    return bigquery.Client(project=PROJECT_ID)


def run_query(client, sql_path):
    query = Path(sql_path).read_text()
    return client.query(query).to_dataframe()


def plot_new_vs_returning(df, output_path):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    axes[0].bar(df["user_type"], df["conversion_rate_pct"], color="#3b82f6", edgecolor="#1e3a8a")
    axes[0].set_title("Conversion Rate (%)")

    axes[1].bar(df["user_type"], df["avg_revenue_per_buyer"], color="#10b981", edgecolor="#065f46")
    axes[1].set_title("Avg Revenue per Buyer (USD)")

    fig.suptitle("New vs Returning Users", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_high_value_segment(df, output_path):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        df["total_revenue"], labels=df["segment"], autopct="%1.1f%%",
        colors=["#f59e0b", "#93c5fd"], startangle=90,
    )
    ax.set_title("Revenue Share: Top 20% Spenders vs Rest", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_device_buyers(df, output_path):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    axes[0].bar(df["device"], df["avg_order_value"], color="#3b82f6", edgecolor="#1e3a8a")
    axes[0].set_title("Avg Order Value (USD)")

    axes[1].bar(df["device"], df["avg_purchase_frequency"], color="#10b981", edgecolor="#065f46")
    axes[1].set_title("Avg Purchase Frequency (orders/buyer)")

    fig.suptitle("Mobile vs Desktop Buyers", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)


def run_chi_square_test(client):
    df = run_query(client, "queries/10_organic_vs_paid_conversion.sql")
    organic = df[df["channel"] == "organic"].iloc[0]
    paid = df[df["channel"] == "cpc"].iloc[0]

    contingency_table = [
        [organic["converted_users"], organic["not_converted_users"]],
        [paid["converted_users"], paid["not_converted_users"]],
    ]
    chi2, p_value, dof, expected = chi2_contingency(contingency_table)

    result = pd.DataFrame([{
        "channel_a": "organic",
        "channel_b": "cpc",
        "chi2_statistic": round(chi2, 4),
        "p_value": round(p_value, 6),
        "significant_at_0.05": bool(p_value < 0.05),
    }])
    return result


def main():
    client = get_client()

    print("Running new vs returning users query...")
    new_vs_returning = run_query(client, "queries/07_new_vs_returning.sql")
    print(new_vs_returning.to_string(index=False))
    new_vs_returning.to_csv(DATA_DIR / "segment_new_vs_returning.csv", index=False)
    plot_new_vs_returning(new_vs_returning, DATA_DIR / "segment_new_vs_returning_chart.png")

    print("\nRunning high-value segment query...")
    high_value = run_query(client, "queries/08_high_value_segment.sql")
    print(high_value.to_string(index=False))
    high_value.to_csv(DATA_DIR / "segment_high_value.csv", index=False)
    plot_high_value_segment(high_value, DATA_DIR / "segment_high_value_chart.png")

    print("\nRunning mobile vs desktop buyers query...")
    device_buyers = run_query(client, "queries/09_mobile_vs_desktop_buyers.sql")
    print(device_buyers.to_string(index=False))
    device_buyers.to_csv(DATA_DIR / "segment_device_buyers.csv", index=False)
    plot_device_buyers(device_buyers, DATA_DIR / "segment_device_buyers_chart.png")

    print("\nRunning chi-square test: organic vs paid conversion...")
    chi_square_result = run_chi_square_test(client)
    print(chi_square_result.to_string(index=False))
    chi_square_result.to_csv(DATA_DIR / "chi_square_test.csv", index=False)

    print("\nAll segment tables, charts, and the chi-square result saved to data/")


if __name__ == "__main__":
    main()

