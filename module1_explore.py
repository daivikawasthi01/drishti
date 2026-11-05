"""Module 1: Event Schema Modeling & Data Exploration."""

from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd
from google.cloud import bigquery

# configure
PROJECT_ID = "drishti-daivik-01"
DATASET = "bigquery-public-data.ga4_obfuscated_sample_ecommerce"
START_DATE = "20201101"
END_DATE = "20210131"

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


def get_client():
    return bigquery.Client(project=PROJECT_ID)


def run_event_overview(client):
    query = Path("queries/01_event_overview.sql").read_text()
    return client.query(query).to_dataframe()


def run_dataset_profile(client):
    query = f"""
    SELECT
      MIN(PARSE_DATE('%Y%m%d', event_date)) AS first_date,
      MAX(PARSE_DATE('%Y%m%d', event_date)) AS last_date,
      COUNT(DISTINCT event_date) AS days_covered,
      COUNT(DISTINCT geo.country) AS countries_covered,
      COUNT(DISTINCT user_pseudo_id) AS unique_users,
      COUNT(*) AS total_events
    FROM `{DATASET}.events_*`
    WHERE _TABLE_SUFFIX BETWEEN '{START_DATE}' AND '{END_DATE}'
    """
    return client.query(query).to_dataframe()


def draw_schema_diagram(output_path):
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    def box(x, y, w, h, label, color="#bfdbfe"):
        rect = mpatches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.1",
            linewidth=1.2,
            edgecolor="#1e3a8a",
            facecolor=color,
        )
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=9)

    box(3.5, 4.25, 3, 1.5, "events_*\n(one row per event)", color="#93c5fd")

    box(0.2, 7, 2.6, 1.2, "event_params\n(REPEATED)\nkey/value pairs")
    box(3.7, 7, 2.6, 1.2, "user_properties\n(REPEATED)\nuser-level attrs")
    box(7.2, 7, 2.6, 1.2, "items\n(REPEATED)\nproducts in event")

    box(0.2, 1, 2.6, 1.2, "device\n(STRUCT)\ncategory, OS")
    box(3.7, 1, 2.6, 1.2, "geo\n(STRUCT)\ncountry, city")
    box(7.2, 1, 2.6, 1.2, "ecommerce\n(STRUCT)\npurchase_revenue")

    for bx in (1.5, 5.0, 8.5):
        ax.annotate("", xy=(5, 5.75), xytext=(bx, 7),
                    arrowprops=dict(arrowstyle="->", color="#1e3a8a"))
    for bx in (1.5, 5.0, 8.5):
        ax.annotate("", xy=(5, 4.25), xytext=(bx, 2.2),
                    arrowprops=dict(arrowstyle="->", color="#1e3a8a"))

    ax.set_title("GA4 events_* Table — Nested Schema Relationships",
                  fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)


def main():
    client = get_client()

    print("Running event overview query (event counts, unique users/sessions)...")
    overview_df = run_event_overview(client)
    print(overview_df.to_string(index=False))
    overview_df.to_csv(DATA_DIR / "event_overview.csv", index=False)

    print("\nRunning dataset profile query (date range, countries, volume)...")
    profile_df = run_dataset_profile(client)
    print(profile_df.to_string(index=False))
    profile_df.to_csv(DATA_DIR / "dataset_profile.csv", index=False)

    print("\nDrawing schema diagram...")
    diagram_path = DATA_DIR / "schema_diagram.png"
    draw_schema_diagram(diagram_path)
    print(f"Saved to {diagram_path}")


if __name__ == "__main__":
    main()
