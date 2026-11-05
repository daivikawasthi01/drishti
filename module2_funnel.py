"""Module 2 (Part 1): Overall 6-Step Purchase Funnel."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from google.cloud import bigquery

PROJECT_ID = "drishti-daivik-01"

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

FUNNEL_STEPS = [
    ("session_start", "Session Start"),
    ("view_item", "View Item"),
    ("add_to_cart", "Add to Cart"),
    ("begin_checkout", "Begin Checkout"),
    ("add_payment_info", "Add Payment Info"),
    ("purchase", "Purchase"),
]


def get_client():
    return bigquery.Client(project=PROJECT_ID)


def run_funnel_query(client):
    query = Path("queries/02_funnel_overall.sql").read_text()
    return client.query(query).to_dataframe()


def reshape_funnel(wide_df):
    row = wide_df.iloc[0]
    labels = [label for _, label in FUNNEL_STEPS]
    users = [int(row[step]) for step, _ in FUNNEL_STEPS]

    df = pd.DataFrame({"step": labels, "users": users})
    df["step_conversion_pct"] = (df["users"] / df["users"].shift(1) * 100).round(2)
    df.loc[0, "step_conversion_pct"] = 100.0
    df["overall_conversion_pct"] = (df["users"] / df["users"].iloc[0] * 100).round(2)
    return df


def plot_funnel(df, output_path):
    fig, ax = plt.subplots(figsize=(9, 5.5))
    bars = ax.bar(df["step"], df["users"], color="#3b82f6", edgecolor="#1e3a8a")

    for bar, users, pct in zip(bars, df["users"], df["overall_conversion_pct"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{users:,}\n({pct}%)",
            ha="center", va="bottom", fontsize=9,
        )

    ax.set_ylabel("Unique Users")
    ax.set_title("Overall Purchase Funnel — Nov 2020 to Jan 2021",
                  fontsize=12, fontweight="bold")
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)


def main():
    client = get_client()

    print("Running overall funnel query...")
    wide_df = run_funnel_query(client)

    funnel_df = reshape_funnel(wide_df)
    print(funnel_df.to_string(index=False))
    funnel_df.to_csv(DATA_DIR / "funnel_overall.csv", index=False)

    chart_path = DATA_DIR / "funnel_overall_chart.png"
    plot_funnel(funnel_df, chart_path)
    print(f"\nSaved funnel table to data/funnel_overall.csv")
    print(f"Saved funnel chart to {chart_path}")


if __name__ == "__main__":
    main()