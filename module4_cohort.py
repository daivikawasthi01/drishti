"""Module 4: Cohort Retention Analysis."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from google.cloud import bigquery

PROJECT_ID = "drishti-daivik-01"

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


def get_client():
    return bigquery.Client(project=PROJECT_ID)


def run_cohort_query(client):
    query = Path("queries/06_cohort_retention.sql").read_text()
    df = client.query(query).to_dataframe()
    df["cohort_month"] = pd.to_datetime(df["cohort_month"]).dt.strftime("%Y-%m")
    return df


def plot_retention_heatmap(df, output_path):
    pivot = df.pivot(index="cohort_month", columns="months_since_first", values="retention_pct")

    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.heatmap(
        pivot, annot=True, fmt=".1f", cmap="RdYlGn", vmin=0, vmax=100,
        cbar_kws={"label": "% Retained"}, ax=ax,
    )
    ax.set_xlabel("Months Since First Purchase")
    ax.set_ylabel("Cohort Month")
    ax.set_title("Purchase Retention by Cohort", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)


def main():
    client = get_client()

    print("Running cohort retention query...")
    df = run_cohort_query(client)
    print(df.to_string(index=False))
    df.to_csv(DATA_DIR / "cohort_retention.csv", index=False)

    plot_retention_heatmap(df, DATA_DIR / "cohort_retention_heatmap.png")
    print("\nSaved: data/cohort_retention.csv")
    print("Saved: data/cohort_retention_heatmap.png")


if __name__ == "__main__":
    main()
