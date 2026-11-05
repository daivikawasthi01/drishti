"""Module 3: Channel Attribution Analysis."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from google.cloud import bigquery

PROJECT_ID = "drishti-daivik-01"

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


def get_client():
    return bigquery.Client(project=PROJECT_ID)


def run_channel_attribution(client):
    query = Path("queries/05_channel_attribution.sql").read_text()
    df = client.query(query).to_dataframe()
    df["channel"] = df["channel"].fillna("(not set)")
    return df


def plot_revenue_bar(df, output_path):
    df_sorted = df.sort_values("total_revenue", ascending=True)
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.barh(df_sorted["channel"], df_sorted["total_revenue"], color="#3b82f6", edgecolor="#1e3a8a")
    ax.set_xlabel("Total Revenue (USD)")
    ax.set_title("Revenue by Channel", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_conversion_vs_aov(df, output_path):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(df["avg_order_value"], df["conversion_rate_pct"],
               s=df["total_revenue"] / df["total_revenue"].max() * 800 + 40,
               color="#3b82f6", edgecolor="#1e3a8a", alpha=0.8)

    for _, row in df.iterrows():
        ax.annotate(row["channel"], (row["avg_order_value"], row["conversion_rate_pct"]),
                    textcoords="offset points", xytext=(6, 6), fontsize=8)

    ax.set_xlabel("Average Order Value (USD)")
    ax.set_ylabel("Conversion Rate (%)")
    ax.set_title("Conversion Rate vs. AOV by Channel\n(bubble size = total revenue)",
                  fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)


def main():
    client = get_client()

    print("Running channel attribution query...")
    df = run_channel_attribution(client)
    print(df.to_string(index=False))
    df.to_csv(DATA_DIR / "channel_attribution.csv", index=False)

    plot_revenue_bar(df, DATA_DIR / "channel_revenue_chart.png")
    plot_conversion_vs_aov(df, DATA_DIR / "channel_conversion_vs_aov_chart.png")

    print("\nSaved: data/channel_attribution.csv")
    print("Saved: data/channel_revenue_chart.png")
    print("Saved: data/channel_conversion_vs_aov_chart.png")


if __name__ == "__main__":
    main()

